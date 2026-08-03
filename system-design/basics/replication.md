# Replication — System Design Notes

> Companion to `partitioning.md`. Partitioning = how data is *spread* across nodes (different data on different nodes). Replication = how *copies* of the same data stay in sync (identical data on multiple nodes). Two independent, orthogonal layers — see "Sharding vs. Replication layering" below, this trips people up constantly.
>
> Template per topic: (1) Explain, (2) Problem solved, (3) Usage scenarios, (4) Mechanism, (5) Pros/cons vs. alternatives, (6) When NOT to use, (7) Failure modes, (8) Scale intuition, (9) Architecture placement, (10) Connection to neighboring components, (11) Interview trigger.

---

## 0. Sharding vs. Replication — the layering (foundational, re-anchored from partitioning discussion)

**A shard holds a slice of the data (different data than other shards). A replica set holds copies of the same data (identical data, for durability). Replication happens *within* a shard, never *between* shards.**

```
Shard 1 (owns key range A-M):  Node 1a (PRIMARY) — Node 1b (secondary) — Node 1c (secondary)
Shard 2 (owns key range N-S):  Node 2a (PRIMARY) — Node 2b (secondary) — Node 2c (secondary)
Shard 3 (owns key range T-Z):  Node 3a (PRIMARY) — Node 3b (secondary) — Node 3c (secondary)
```

- All RF copies of a given piece of data stay within the *same* shard's replica set. A document in range A–M has all its copies on 1a/1b/1c — never touches Shard 2 or 3.
- **Failover is per-shard, independent.** Shard 1's primary dying triggers an election only among 1a/1b/1c. Shard 2 and 3 are completely unaffected — there is no cluster-wide election, only N independent elections scoped to each shard.
- **Write bottleneck is per-shard, not cluster-wide.** Within one shard, adding secondaries does NOT increase that shard's write throughput (secondaries don't accept writes in MongoDB — read capacity + durability only). The actual fix for write scale is **adding more shards**, each with its own primary — cluster-wide throughput scales roughly linearly with shard count, provided the partition key distributes evenly (ties directly back to the partitioning notes — skewed keys mean one shard's primary bottlenecks while others idle).
- **Sharding vs. partitioning terminology (tie-in):** partitioning is the general concept (can happen on a single node, e.g. Postgres table partitioning — no distribution, just query/maintenance efficiency). Sharding = partitioning applied across multiple independent machines for horizontal scale. The partitioning *scheme* (hash-based, range-based, consistent hashing) is the algorithm answering "which shard does this key belong to?" Consistent hashing isn't an alternative to sharding — it's a mechanism that *implements* sharding.
- **What "a shard" means differs by scheme:**

| | Consistent hashing | Directory-based (MongoDB) |
|---|---|---|
| What is "a shard" | A physical node (or its replica group) | A shard = a whole replica set (multiple nodes) |
| How is "which shard owns key X" decided | Computed on the fly — hash(key), walk the ring | Looked up — config servers' range→shard table |
| Where does that decision info live | Nowhere persisted — recomputed each time from hash function + current ring membership (known via gossip) | Explicitly persisted in config servers, cached by routers, invalidated via chunk version numbers |

---

## 1. Leader-Based (Primary-Secondary) Replication

**Explain:** One node (leader/primary) accepts all writes for a given shard/replica set. It replicates to followers/secondaries.

**Problem solved:** A single, unambiguous ordering of writes — because one node decides "what happened, in what order," strong consistency comes almost for free; no concurrent-write ambiguity to resolve at write time.

**Real system — MongoDB replica set:** Each shard = a replica set, typically primary + 2 secondaries. All writes for a chunk go to that shard's current primary. Secondaries pull the primary's **oplog** (capped collection logging every write) and replay it. Reads default to the primary (`readPreference: primary`); reading from secondaries is opt-in and explicitly risks staleness — MongoDB makes you say so explicitly rather than surprising you.

**Mechanism — failover:** Primary down → secondaries detect via missed heartbeats → Raft-like **election** among that shard's own nodes only → node with most up-to-date oplog + majority vote becomes new primary. The sharding directory (config servers) is untouched by this — from its perspective "Shard B" still exists, just served by a different node internally. Majority requirement specifically prevents split-brain (two primaries believing they're primary simultaneously) during a partition.

**Pros vs. leaderless:** Simple mental model, strong consistency by default, minimal write-time conflict handling needed.

**Cons vs. leaderless:** Per-shard write bottleneck (see §0); election isn't instant — real availability gap (seconds) for that shard's writes during failover.

**When NOT to use:** Extremely write-heavy workloads a single primary can't keep up with; multi-region active-active writes where every region needs local write acceptance without round-tripping to one "true" primary (relevant to multi-region ALB/Global Accelerator work — leader-based typically means one true write region, others read-replica or forwarding).

**Failure mode:** Split-brain risk if a partition isolates the primary from majority but a client can still reach it — majority-election requirement is the specific defense.

**Interview trigger:** "Design a system needing strict ordering / single source of truth" → leader-based, name the failover gap as the explicit cost.

---

## 2. Leaderless (Dynamo-Style) Replication

**Explain:** Any of a key's RF replicas can accept a write — no primary. Consistency enforced at read time via quorum overlap, not write-time ordering.

**Problem solved:** Removes the single-writer bottleneck AND the failover-gap availability problem — a down/slow replica just means routing around it, no election needed.

**Real system — Cassandra/DynamoDB:** For a key, its RF replicas (found via ring-walk from the partitioning notes) are equal peers, no primary among them.

**Mechanism — who triggers replication (the coordinator, per-request):**
1. Client connects to **any** node — that node becomes **coordinator** for this one request (not a fixed role; chosen fresh each time).
2. Coordinator computes, via consistent hashing, which RF nodes own this key.
3. Sends the write to all of them **in parallel, synchronously, as part of handling this request** — not a background push initiated later.
4. Waits for **W** acknowledgments, then responds to client.

There is no "shard" in the MongoDB sense here — no fixed ownership hierarchy, no primary. The RF nodes owning a key are an analogous *grouping* but with no leader within it.

**Pros vs. leader-based:** No single-node write bottleneck (parallelizes across RF replicas), no failover gap, naturally suited to multi-region active-active.

**Cons vs. leader-based:** Genuine possibility of conflicting concurrent writes to the same key with no leader to serialize them (see §4); consistency is tunable, not automatic — trusts you to pick R/W appropriately.

**When NOT to use:** Anything where "two concurrent writes, pick one" is unacceptable without careful app-level handling (e.g., raw bank balance) — hence systems like CockroachDB layer Raft-based consensus on top instead of raw Dynamo-style leaderless replication for that use case.

**Side-by-side (anchor table):**

| | MongoDB (leader-based) | Cassandra/DynamoDB (leaderless) |
|---|---|---|
| Who accepts writes | One primary per shard | Any of RF replicas, via per-request coordinator |
| Write scale limit | Bounded by one primary's throughput per shard | Scales with RF and cluster size, no per-partition single-writer cap |
| Failover | Election, brief unavailability window | None needed — route around the down node |
| Consistency | Strong by default | Tunable via R/W; eventual unless quorum enforced |
| Conflict handling | Rare — single writer serializes | Real — needs LWW (default) or app-level merge |
| Best fit | Single-region / strict-ordering workloads | Multi-region active-active, very high write throughput |

**Interview trigger:** Directly parallels your own multi-region active-active work with ALB + Global Accelerator — that's the application-layer version of what leaderless replication solves at the storage layer. Worth stating explicitly if it comes up.

---

## 3. Why Conflicts Happen Even Though the Coordinator Replicates — Two Distinct Failure Shapes

This resolves the apparent contradiction: "if the coordinator fans out to all N replicas, why would nodes ever disagree?"

**Shape A — transient divergence (self-healing, not true data loss):**

RF=3 (Node1/2/3), W=1. Client A's write → Coordinator-1 → fans out to all 3, but Node3 is momentarily unreachable. Coordinator-1 already got 1 ack (W=1 satisfied) and tells the client "success" **while the write is still in flight / pending to Node3** (hinted handoff kicks in — see §6). Meanwhile Client B's write → Coordinator-2 → reaches all 3 fine, including Node3. Now: Node1 & Node2 have both writes and agree via LWW; Node3 only has Client B's write — not because of conflict, just because it hasn't received Client A's yet. A read hitting only Node3 (if R=1) sees stale data temporarily, until read repair or anti-entropy fixes it.

**The original write's coordinator does NOT trigger reconciliation** — its job ends once it fans out and gets enough acks. Reconciliation is triggered later, by a *different* mechanism: a future read's opportunistic read repair, or a scheduled anti-entropy pass.

**Shape B — real, permanent loss under LWW (the one that actually matters for a cart-style example):**

Counterintuitive: this can happen **even when replication works perfectly and every node fully agrees with every other node.** If Client A's and Client B's writes both reach all 3 nodes cleanly (no network issue at all), every node independently applies the same LWW rule — compare timestamps, keep the later, discard the other. All 3 nodes converge to the *same* winner — **zero cross-node disagreement** — and yet the loser's data is permanently gone, because LWW treats "two different values written to the same key" as one overwriting the other, not as two things to merge. This is not a replication bug; it's LWW working exactly as designed. **The real fix is data modeling** — don't store a cart as one opaque blob column; model independently-updatable items (rows/columns per item) so concurrent writes to *different* items never collide on the same key at all.

---

## 4. Conflict Resolution — LWW vs. Vector Clocks vs. CRDTs

### ⚠️ Correction to internalize: which real systems use which mechanism

<cite index="0-1">Vector clocks were proposed in the original Dynamo paper, but most Dynamo-family databases (Cassandra, DynamoDB) actually use Last-Write-Wins as their default conflict resolution mechanism in practice</cite> — NOT vector clocks. **Riak** (built directly on the Dynamo paper by ex-Amazon engineers) is the real production system implementing vector clocks with client-exposed conflict resolution. If an interviewer asks "which database uses vector clocks," the accurate answer is Riak, not Cassandra/DynamoDB.

<cite index="0-1">Cassandra's designers deliberately avoided vector clocks by breaking a row into independently-updatable columns</cite> — so a naive LWW-on-an-opaque-blob failure mode (silently discarding one whole conflicting update) isn't the exposure they were designing around in the same way Riak was.

### Last-Write-Wins (Cassandra/DynamoDB actual default)

Compare wall-clock timestamps; keep the later, discard the other. **The database resolves it automatically — no app involvement.** <cite index="1-1">Data may be overwritten on write contention, and odds of data loss are magnified by inevitable server clock drift.</cite> Risk is real and silent — see Shape B above.

### Vector Clocks (Riak's actual mechanism)

Each replica tags its version with a vector clock — a set of counters, one per node/actor that has written to it. Worked example (cart):

1. Client A "add Book A" coordinated by node X → stored `[Book A]`, clock `{X:1}`.
2. Client B "add Book B" coordinated by node Y, **without first reading X's version** → stored `[Book B]`, clock `{Y:1}`.
3. A read hits both X and Y, compares clocks. **Dominance rule:** clock P dominates clock Q only if P's count ≥ Q's for every entry, and greater for at least one. Here neither `{X:1}` nor `{Y:1}` dominates the other → **genuine concurrent conflict** → both versions ("siblings") returned to client.
4. Contrast: if Client B had first *read* X's version before writing (coordinated by node Z), the new clock would be `{X:1, Z:1}` — this *does* dominate plain `{X:1}`, so the system knows it's a legitimate sequential update, not a conflict, and safely discards the old version automatically.

<cite index="2-1">When a client next reads a key with siblings, the database returns both versions and lets the client merge the fields without losing either update.</cite>

### Who actually resolves the conflict, and who decides the strategy

- **LWW:** (Last-Write-Wins)database resolves automatically at write-time comparison — no app involvement, real data-loss risk.
- **Vector clocks:** database *detects and surfaces* the conflict but does not resolve it — <cite index="3-1">vector clocks only tell you a conflict occurred, not how to resolve it.</cite> Resolution pushed to the **application** at read time — app merges (e.g., union cart items) and writes back; that write's vector clock dominates both prior siblings, becoming the new authoritative version, propagated via read-repair/anti-entropy.
- **CRDTs:** the **data structure itself** resolves it automatically — no app code, no per-conflict human decision.
- **Who decides which strategy to use:** a data-modeling decision made upfront by whoever designs the schema — not chosen per-conflict at runtime. Cassandra is architecturally LWW; you avoid its data-loss risk by modeling independently-updatable columns/rows, not by switching mechanisms.

### CRDTs (Conflict-Free Replicated Data Types)

Data structures engineered so merging divergent replicas is mathematically well-defined, deterministic, and always converges to the same correct result — no app logic, no possibility of a "wrong" merge.

**Example — G-Counter (grow-only counter),** e.g. counting likes across 3 nodes. Each node keeps its *own* counter for increments it personally handled:
```
Node X's view: {X: 5, Y: 0, Z: 0}
Node Y's view: {X: 0, Y: 3, Z: 0}
```
Merge rule: **component-wise maximum** → `{X:5, Y:3, Z:0}` → total = sum = 8. Commutative, associative, idempotent — merge in any order, any number of times, always converges correctly. This "always converges to the same result regardless of merge order" property = **strong eventual consistency**.

**Shopping cart as a CRDT (OR-Set — observed-remove set):** <cite index="4-1">adding items A and B can happen on any node in any order — the end result is simply both items in the cart; removal is modeled as a "negative add" rather than a true delete</cite> — merge is just set union, unambiguous regardless of order/repetition.

**Why CRDTs aren't used everywhere:** <cite index="4-1">it's often not easy to model real-world data as a CRDT — for many objects it involves too much modeling effort, so vector clocks with client-side resolution end up considered good enough in practice.</cite> CRDTs work cleanly for sets/counters; they don't generalize to arbitrary business objects (no obvious mathematically-correct "union" of two conflicting bank transactions).

**Interview trigger for this whole section:** "Design a shopping cart" or similar — expected to name LWW's real risk, propose either app-level merge (Riak-style) or a CRDT (OR-Set) as the fix, and explain why a naive single-blob LWW model is the actual bug, not the replication.

---

## 5. Quorum Consistency — R + W > N

**The claim:** if R + W > N, every read is guaranteed to overlap with the most recent successful write on at least one replica.

**Derivation (pigeonhole, not magic):** N=3, W=2, R=2 (R+W=4>3). A write succeeds once any 2 of 3 replicas ack — the "write set," size 2. A read queries any 2 of 3 — the "read set," size 2. Can these be fully disjoint? 2+2=4 slots needed, only 3 nodes exist → by pigeonhole, at least one node must appear in both sets. That shared node has the latest write; whatever the read set returns, reconciliation (timestamp/vector-clock comparison across what was returned) surfaces it.

**When R+W ≤ N (risky configs):** N=3, W=1, R=1 (sum=2, not >3). No guaranteed overlap — a read can easily hit a replica that hasn't received the write yet (replication in flight, or pending hinted handoff). This is exactly Shape A staleness — not broken, just no overlap guarantee, traded deliberately for max speed/availability.

**Named configurations:**
- **W=N, R=1** ("write-heavy safety") — slow, unavailable if any replica down; but any single-replica read is guaranteed current.
- **W=1, R=N** ("read-heavy safety") — fast, available writes; but every read touches all N and reconciles — slow reads, always current.
- **W=QUORUM, R=QUORUM** (majority, `⌊N/2⌋+1` each) — balanced default. N=3 → quorum=2 → W=2,R=2. Cassandra's most common production setting (`CONSISTENCY QUORUM`); tolerates 1 node down on either op, guarantees overlap.
- **W=1, R=1** ("ANY"-style max availability) — fastest, most fault-tolerant, zero overlap guarantee — deliberate eventual-consistency trade, appropriate when downstream merge logic (CRDT) fixes it anyway.

**Nuance to hold precisely:** R+W>N guarantees you'll **see** the latest write among returned versions — it does NOT by itself resolve which is "latest" under a genuine concurrent conflict. Quorum overlap = visibility guarantee. Conflict resolution (LWW/vector-clock/CRDT) = a separate mechanism layered on top of whatever the overlapping read surfaces. Don't conflate "I'll see the recent stuff" with "I know how to pick among what I see."

---

## 6. Self-Healing Mechanisms — Hinted Handoff, Read Repair, Anti-Entropy

Three distinct mechanisms, each solving a different gap — commonly lumped together but worth precise separation:

**Hinted handoff** — solves: replica **known down at write time**. Coordinator can't reach Node3 → a hint ("this write belongs to Node3") is stored elsewhere → delivered directly once Node3 rejoins. Proactive, fast, catches up a returning node without waiting for a read or scheduled job. <cite index="0-1">In Cassandra specifically, hinted writes generally don't count toward satisfying your write consistency level except at consistency ANY</cite> — hinted handoff aids eventual convergence but doesn't relax your actual W guarantee the way it does in the original Dynamo design.

**Read repair** — solves: staleness discovered **opportunistically during a normal read**. If R replicas return differing versions, the coordinator detects the mismatch while reconciling before responding to the client, and pushes the correct value to whichever replica(s) were behind. Only fixes keys that actually get read.

**Anti-entropy (Merkle trees)** — solves: staleness on keys that **never get read and were never part of a hinted handoff** (e.g., a node down long enough that hints expired). A **background, scheduled process** — periodically compares a Merkle tree (hash tree; each leaf hashes a data chunk, each parent hashes its children) between replicas. If root hashes match, everything below is identical — no further comparison. If they differ, recurse into just the differing branches. This makes convergence practical at scale — only actually-differing data moves, not the whole dataset.

**How they stack:** hinted handoff = fast recovery for a known, temporary outage. Read repair = opportunistic, accessed-keys-only. Anti-entropy = backstop guaranteeing eventual convergence even for cold keys nobody reads — without it, "eventually consistent" is aspirational, not guaranteed.

---

## 7. Sync vs. Async Replication

**Explain:** Governs *when* a write is acknowledged relative to replica confirmation — the leader-based analog of the W setting in leaderless systems.

- **Synchronous:** leader waits for replica(s) to confirm before acknowledging client. Zero loss if leader dies immediately after acking.
- **Asynchronous:** leader acknowledges immediately on local persist, replicates in background. Faster, but a real window where leader has data replicas don't.

**Mechanism — MongoDB's `writeConcern` (the concrete knob):**
- `w: 1` — ack once primary has it (async to secondaries) — fast, but if primary dies before replicating, the "successful" write is gone.
- `w: majority` — ack once a majority of the replica set has it (sync-ish) — guarantees the write survives an election, since a majority-elected new primary is guaranteed to have seen any majority-acknowledged write.
- Direct analog to leaderless R/W — same trade-off, different name, defaulting to leader-based semantics.

**The failover connection (critical):** if replication is async and the primary dies **right after acknowledging but before replicating**, the newly-elected primary (from secondaries) **never received that write** — silently lost despite "success" being returned to the client. This is exactly why production MongoDB deployments handling anything important use `w: majority`, not default `w: 1` — it directly closes the data-loss gap inherent to leader-based failover.

**Pros/cons:** Sync = no loss (up to quorum), but higher latency + availability tied to replica health. Async = low latency, primary stays available independent of replica health, but real silent-loss window on failure.

**Distinct failure mode — replication lag:** under async with heavy write load, secondaries can meaningfully fall behind. A client reading from a secondary (if allowed) sees stale data — an ongoing steady-state staleness, distinct from the one-time failover data-loss window.

**Interview trigger:** "Design a payments ledger / anything loss-intolerant" → expected answer explicitly reaches for sync/majority-acknowledged writes, and names the specific scenario (primary dies mid-write) that sync protects against.

---

## 8. CAP Theorem (Properly) and PACELC

**The precise claim (not "pick 2 of 3"):** Partition tolerance isn't optional — real systems will experience partitions. The actual decision is: **during an active partition, choose Consistency or Availability.** No partition → a well-designed system can offer both simultaneously; CAP says nothing about the non-partition case.

**Concretely, in systems now known end-to-end:**
- **MongoDB during a partition** isolating primary from majority of secondaries: primary steps down (can't get majority for writes) → shard unavailable for writes until new primary elected on majority side. **Chooses C over A.**
- **Cassandra during a partition** with W=1: both sides keep accepting writes independently, diverge, reconcile later. **Chooses A over C.**

**PACELC (the more complete, more useful framing — worth leading with to signal depth):** if **P**artitioned → choose **A**vailability or **C**onsistency; **E**lse (no partition) → choose **L**atency or **C**onsistency. This second half explains the *normal*, non-partitioned case — nearly all the time. Why does Cassandra default to eventual consistency even on a perfectly healthy network? Not CAP (no partition happening) — it's that waiting for full quorum/majority replication **adds latency**, and Cassandra's designers chose low latency over strong consistency even in the common case. This is the same W=1/R=1 vs. W=majority/R=majority choice from §5 — a **latency-vs-consistency** decision (PACELC's "LC"), not partition-driven at all. CAP alone can't explain why a healthy, fully-connected Cassandra cluster still defaults to loose consistency; PACELC can.

**Interview trigger:** Any "explain CAP" question — give the correct partition-scoped claim, one concrete C-favoring example (MongoDB primary stepping down) and one A-favoring example (Cassandra staying available) from systems you know internally, then **volunteer PACELC unprompted** to explain the non-partition default-consistency-level choice. This is the Senior-vs-Staff signal on this specific question.

---

## Quick self-test (answer before moving on)

1. Why can two nodes fully agree with each other (no divergence) and still have permanently lost data? (Shape B)
2. Derive, from pigeonhole, why R=2/W=2/N=3 guarantees overlap but R=1/W=1/N=3 doesn't.
3. Name the real production system that uses vector clocks, and the two that use LWW by default instead.
4. What's the difference between what read repair fixes and what anti-entropy fixes?
5. State CAP's actual partition-scoped claim, then explain — using PACELC, not CAP — why Cassandra defaults to eventual consistency even with a perfectly healthy network.

## Open threads / to revisit
- Next system-design pillar after replication: not yet decided — candidates include caching (Redis/Memcached, cache-aside vs write-through, cache stampede), consensus deep-dive (Raft mechanics beyond "majority vote"), or moving into a concrete system (Cassandra or DynamoDB) end-to-end using this template.
- Revisit from partitioning.md: enterprise-ID compound-key fix — closer to range-based or directory-based mentally? (still open)
