# Partitioning — System Design Notes

> Template applied per topic: (1) Explain it, (2) Problem it solves, (3) Usage scenarios, (4) Mechanism, (5) Pros/cons vs. alternatives, (6) When NOT to use it, (7) Failure modes, (8) Scale/latency intuition, (9) Architecture placement, (10) How it connects to neighboring components, (11) Your own production war story, (12) Disguised interview question it answers.

## Mental model — two independent axes

Before the individual schemes: partitioning approaches split along two axes, not four parallel categories.

- **Axis 1 — How is the mapping determined?**
  - *Computed/formulaic* (hash-mod-N, consistent hashing) — no metadata store needed; any node can independently calculate ownership.
  - *Explicitly assigned/looked-up* (range-based, directory-based) — something recorded the mapping; it wasn't derived by a formula.
- **Axis 2 — What's the unit being mapped, and is it structured?**
  - *Ordered/structured* (range-based) — units are contiguous slices of sorted key space, and can only change via splits/merges.
  - *Arbitrary/unstructured* (pure directory-based) — units can be anything, reassigned freely with no ordering constraint.

MongoDB sits at "range-structured units, directory-style unconstrained reassignment of those units to shards" — it's a hybrid, not a failure to categorize.

---

## 1. Hash-Based Partitioning (`hash(key) mod N`)

**Explain:** Key → hash → `mod N` → deterministic node assignment.

**Problem solved:** Even distribution of data/load without needing to know data structure ahead of time.

**Usage scenarios:** Basic KV stores, naive early sharding, anywhere needing O(1) "which node" computation.

**Mechanism:** Client/router computes `hash(key) % N`, sends request directly — pure computation, no coordination for lookups.

**Pros:** Simple, no metadata service, fast, uniform distribution with a good hash function.

**Cons:** Changing N remaps ~most keys (e.g., 4→5 nodes remaps ~80%) — massive reshuffle on every scale event.

**When NOT to use:** Any system expecting dynamic cluster resizing — i.e., almost everything in production. Mostly a stepping stone to consistent hashing.

**Failure mode:** Even a temporary node removal shifts `mod N`, cascading rehash to surviving nodes too.

**Scale intuition:** Computation is cheap; the cost is entirely in the reshuffle event, proportional to total data size.

**Architecture placement:** Routing layer — client-side or a proxy/coordinator in front of the cluster.

**Interview trap:** "How would you shard this?" → "hash mod N" → interviewer asks "what happens when you add a node?" — must pivot to consistent hashing immediately.

---

## 2. Range-Based Partitioning

**Explain:** Keys sorted; key space split into contiguous ranges, each owned by a node (e.g., users A–F → node 1).

**Problem solved:** Efficient range queries — "all events between T1 and T2" hits contiguous nodes instead of scattering (which hashing would force).

**Usage scenarios:** Time-series (InfluxDB, ClickHouse by time), Bigtable/HBase (by row key), Spanner, CockroachDB.

**Mechanism:** Metadata layer tracks range boundaries. Ranges **split** when they grow too large (threshold ~64–512MB), potentially moving half to a new node; can **merge** when small. Metadata stays compact because unit count is proportional to `total data / range size threshold`, not per-key.

**Pros:** Efficient range scans, natural for time-ordered/lexicographic data, splits are localized (not whole-cluster reshuffle).

**Cons:** High hotspot risk with skewed keys (incrementing IDs, "now" timestamps) — all new writes land on one range until it splits.

**When NOT to use:** Point-lookup-only workloads with high write skew — hash-based would distribute load better.

**Failure mode:** A hot range's node bottlenecks faster than splits can react — write latency spikes concentrated on one node while rest of cluster idles.

**Scale intuition:** Ranges dynamically split at a size threshold, not fixed upfront.

**Architecture placement:** Requires a metadata/routing service tracking current boundaries — structurally similar to directory-based (range-based is "directory-based where the directory happens to be ordered ranges").

**Interview trigger:** "Design a time-series metrics/logging platform" → range-by-time + hotspot mitigation is the intended path.

---

## 3. Consistent Hashing (+ Virtual Nodes)

**Explain:** Nodes and keys both hashed onto a circular space (ring). A key belongs to the first node found walking clockwise from its position. Node add/remove only affects keys between it and its predecessor — not the whole ring.

**Problem solved:** Minimal data movement on cluster resize (fixes hash-mod-N's near-total reshuffle).

**Usage scenarios:** Cassandra, DynamoDB, Riak, CDN routing, client-side sharding for Memcached (which has no native clustering logic).

**Mechanism — how a key is actually located:**
- `hash(key)` → a ring position. Walk clockwise; first vnode marker hit owns the key. The vnode label (e.g., `B_1` vs `B_2`) is arbitrary — no meaningful relationship between the key's hash and which of a node's several vnodes gets hit; purely positional.
- **Replicas (RF=N):** continue walking clockwise from that point, taking the next N−1 **distinct physical nodes**, skipping any vnode belonging to an already-selected physical node. This "skip if already selected" rule is essential — it guarantees replicas land on separate physical machines, so losing one node can't wipe out multiple copies at once.

**Virtual nodes:** Plain consistent hashing with few physical nodes gives uneven ring distribution by chance. Fix: each physical node hashed onto many points (100–256 in real systems). Benefits:
1. Smooths out ownership distribution.
2. On node failure, load spreads across *many* neighbors instead of dumping entirely onto one — converts a concentrated shock into a diffused, absorbable one (prevents cascading failure where one overloaded neighbor is more likely to fail next).

**Re-replication on permanent node loss:** If a node fails permanently, its keys drop from RF=N to RF=N−1 for every key it held. The system must find a **new distinct physical node** (walk clockwise, skip already-holding nodes) to restore RF=N — this is what "redistribution on failure" actually means: not the ring rearranging ownership abstractly, but re-replication to restore durability. This is not optional — under-replicated data is one more failure away from loss.

**Precondition this depends on:** Cluster must have meaningfully more physical nodes than RF. With exactly N=RF nodes, losing one node makes restoring full replication *impossible* until an operator adds a replacement — cluster runs degraded (RF−1) in the interim. This is why production clusters run dozens–hundreds of nodes against RF=3.

**Pros:** Minimal reshuffling on scale events, supports incremental scale-out, vnodes give even distribution + graceful failure spreading.

**Cons:** More complex than hash-mod-N; some movement still occurs on scale (not zero); no native range-query support (keys scattered by design).

**When NOT to use:** Workloads needing efficient range scans.

**Failure mode:** With vnodes — graceful load redistribution across many neighbors. Without vnodes — one physical neighbor absorbs 100% of the failed node's load → cascading failure risk.

**Scale intuition:** Adding one node to an N-node ring with vnodes moves ~`1/N` of total data — proportional and predictable.

**Architecture placement:** Lives in client library or routing/coordinator layer. In leaderless systems (Cassandra), every node knows the full ring topology via gossip (see below).

**Known limitation (enterprise-ID / tenant-ID as partition key):** `hash(enterpriseID)` always lands on the same node/replicas. Consistent hashing guarantees clean rebalancing and stable ownership — it says nothing about whether one key's data volume is reasonable for one node. A huge tenant collapsing onto one node/replica set is a hotspot triggered by data-size skew. **Fix: compound/composite partition key** — `(enterpriseID, subEntityID)` e.g. `(enterpriseID, studentID)` — so one tenant's data spreads across many partitions instead of one.

**Interview trigger:** "Design a distributed cache / URL shortener / DynamoDB" — near-mandatory ingredient whenever "scale without downtime" is in scope.

---

## 4. Directory-Based Partitioning

**Explain:** A separate lookup service explicitly maps keys/ranges to owning nodes — no formula, just an explicit, freely reassignable table.

**Problem solved:** Maximum rebalancing flexibility — any scheme (move one hot key to its own node, migrate arbitrarily) is possible since ownership is just data in a table.

**Usage scenarios:** MongoDB sharding (config servers + `mongos` routers), Bigtable (root/metadata table → tablet locations).

**Mechanism — MongoDB as the concrete case (this is the important nuance from the Q&A):**
- **The directory = the config servers** — the single authoritative source of truth, itself replicated for availability.
- **The router's (`mongos`) local cache is NOT a second directory** — it's a cached copy of (part of) the same directory, held locally to avoid hitting config servers on every request.
- **Granularity: NOT per-document-ID.** The directory maps `shard_key_range → shard` at **chunk** granularity (~64–128MB per chunk) — a hybrid of range-based structure (ordered, split/merge-constrained units) with directory-style (unconstrained) reassignment of those chunks to shards. A pure per-key directory would need metadata proportional to key count (billions of entries) — impractical, which is why no directory-based system actually runs at that granularity.
- **Write path:** normal writes do NOT touch the config servers. The router already has the range→shard mapping cached and writes straight to the correct shard.
- **Cache invalidation:** each chunk has a **version number**. If a chunk migrates, the config servers' table updates; a router with a stale cached version gets rejected by the shard ("you're out of date"), refreshes from config servers, retries. Version-check-and-reject-then-refresh, not a push notification.
- **Node removal (graceful):** decommissioning a shard means **draining** it first — migrating all its chunks to other shards while still healthy — then removing its directory entry once empty. Directory-based systems generally don't self-heal from an *unexpected* crash the way gossip-based leaderless systems do; that requires operator/orchestration intervention.
- **Hotspot handling:** isolating a hot key/range onto its own dedicated shard = updating the directory's entries for that range to point at the new shard; routers pick this up via the version-check-and-refresh mechanism.

**Sharding vs. replication — layering (important distinction):** Sharding splits *data* across independent shards for horizontal scale. Replication means each shard is *itself* a replica set (e.g., primary + 2 secondaries in MongoDB), not a single machine — for durability/failover. Nested: cluster → shards → each shard is a replica set → each replica set is nodes. When one node inside a shard's replica set crashes, the replica set handles it internally (Raft-like election of new primary); **the directory never changes** — it only tracks shard-level mapping, not which node within a shard is currently primary. Sharding and replication solve two separate problems (scale vs. durability) at two separate layers.

**Pros:** Total rebalancing flexibility, easy to reason about/debug (just inspect the table).

**Cons:** Directory is a potential SPOF/bottleneck unless replicated (which itself needs consensus, e.g. Raft); every request pays a lookup cost unless cached; cache invalidation on rebalancing is a real problem to solve.

**When NOT to use:** When you want to avoid operating a separate coordination service — smaller systems often lean on consistent hashing instead (no metadata store needed at all).

**Failure mode:** Directory service down/stale → routing breaks cluster-wide. Why directory services are themselves consensus-replicated (config server replica set).

**Scale intuition:** The directory itself must handle lookup QPS at cluster-wide request rate unless heavily cached — often the actual bottleneck people underestimate.

**Architecture placement:** Dedicated service/cluster between clients and data nodes — analogous to a DNS layer.

**Interview trigger:** "Design MongoDB's sharding" / "how do you handle a hot key" — directory-based is the clean answer for pinning one hot key to its own shard, something consistent hashing structurally can't do (a key's location is tied to its hash, not to an arbitrary override).

---

## 5. Hotspots (cross-cutting failure mode, not a scheme itself)

**Explain:** Disproportionate load (read/write/storage) concentrated on one node/partition, defeating the purpose of partitioning. A failure mode any of the above 4 schemes can produce under skewed real-world traffic.

**Problem/gap it represents:** The distance between "theoretically even distribution" and actual traffic patterns, which rarely match uniform assumptions.

**Usage scenarios where it bites:** Celebrity/viral user (Twitter/Instagram classic), sequential/monotonic keys (auto-increment IDs, "now" timestamps), viral post's comment section, oversized tenant (enterprise-ID case above).

**Two distinct hotspot shapes — need different fixes:**

- **Case A — single row is hot (read-heavy):** e.g., celebrity profile read constantly. Only one record — nothing to split. **Fix: caching in front (Redis/Memcached)** to absorb reads before hitting the partition, or read replicas. Salting does NOT apply here.
- **Case B — one partition key has too many rows under it (write/storage-heavy):** e.g., "#worldcup" hashtag, or an oversized tenant's records. **Fix: salting or compound keys.**

**Salting mechanics (precise, since this is easy to get wrong):**
- The salt is part of the **actual physical write key**, not hidden only in a hashing step. Writing under `#worldcup` picks a salt (random or round-robin 0–9) and writes to the physical key `worldcup_shard3`. *That* physical key is what gets hash/consistent-hashed — deliberately landing on a different ring position/node than `worldcup_shard7`, spreading one logical key across N physical nodes.
- **Reads fan out and merge:** querying "all #worldcup tweets" means querying all N physical keys in parallel and merging client-side. Only makes sense for "give me a *set* of items" queries — NOT for an exact single-record point lookup by ID (that's Case A, not a salting scenario at all).
- Requires either (a) client knows the fixed salt scheme (always 0–9) to fan out deterministically, or (b) a secondary index of "which salts have data for this logical key" — functionally a mini directory layer on top of consistent hashing, not a replacement for it.
- **Compound key (enterprise-ID case) vs. salting (hashtag case) — same underlying idea, different framing:** both spread one oversized logical unit across multiple physical partitions by extending the key. Compound key `(enterpriseID, studentID)` is the natural fit when there's already a meaningful sub-entity to key on; salting with an arbitrary/random suffix is the fallback when no natural sub-key exists (a hashtag has no inherent substructure to partition by).

**Failure mode if unaddressed:** Hot node's latency degrades → clients retry → retries add more load to the already-hot node → thundering-herd-style collapse concentrated on one machine while rest of cluster is fine.

**Scale intuition:** A single node typically maxes out in the tens-of-thousands of ops/sec depending on hardware; if one key receives >10% of cluster traffic, that's almost certainly a hotspot regardless of scheme.

**Architecture placement:** Cross-cutting — shows up at partitioning layer (which scheme), caching layer (mitigation), and monitoring layer (must detect hotness before reacting — ties to OTel/observability).

**Interview trigger:** Nearly any "design X at scale" with a celebrity/viral element (Twitter, Instagram, YouTube) is quietly testing whether you raise hotspots + the appropriate fix *unprompted*. High-signal moment for Staff-level bar.

---

## Gossip Protocol (supporting mechanism for consistent hashing in leaderless systems)

**Explain:** Decentralized way for nodes to learn cluster state (who's alive, who joined/left, ring topology) with no central coordinator/directory.

**Mechanism:** Periodically (e.g., every ~1s), each node picks 1–3 random peers, exchanges its current view of cluster state; each side merges, keeping the newer (version-stamped) info. Spreads epidemic-style in ~`O(log N)` rounds. Probabilistic, eventually consistent — different nodes can briefly disagree during a topology change.
Every node ends up holding a full, locally-cached copy of the cluster's ring topology — which physical nodes exist, their virtual node positions (token ranges) on the ring, and their current health status (alive, suspected-down, actually-down). This local copy is what lets any node act as coordinator for any key, computing ownership itself via the ring-walk, with zero need to ask a separate directory service.

**Where it fits with consistent hashing:** In leaderless systems (Cassandra), there's no config server/directory by design — avoiding the SPOF/bottleneck a directory introduces. Every node needs to know current ring topology to route requests/compute replicas correctly. Gossip is how a new node's join, or a failed node's departure, propagates to every node's local ring view — no central authority needed.

**Direct contrast:** MongoDB (directory-based) = one authoritative source, explicit, strongly consistent, but a coordination bottleneck/SPOF risk. Cassandra (gossip + consistent hashing) = no authoritative source, eventually-consistent local views per node, no bottleneck, but genuinely eventually consistent — part of why leaderless systems lean on quorum reads/writes and read-repair to paper over transient disagreement right after a topology change.

**Interview trigger:** "How does Cassandra know its own topology without a config server like MongoDB has?" — gossip is the direct answer.

---

## Open threads / to revisit
- Replication concepts next: leader-based vs. leaderless, R+W>N quorum math, conflict resolution (LWW vs. vector clocks vs. CRDTs).
- Revisit: is the enterprise-ID compound-key fix closer to range-based or directory-based mentally? (Answer worth writing out here after next session.)



It's in `replication.md` §0 as a comparison table, but not in `partitioning.md` itself — and since the confusion started as a partitioning question, it belongs there too. Here's a self-contained write-up to paste in.

---

### What "a shard" means, by partitioning scheme (and how leader-based replication sits on top)

The confusion was really three separate things getting collapsed into one — worth keeping them as three explicitly separate layers:

**Layer 1 — What is a shard, under each scheme:**

- **Consistent hashing:** a shard **is a physical node**. There's no separate "shard" concept distinct from the node itself — the ring just tells you which node owns a key. (With replication, RF copies live on RF *distinct* physical nodes found by walking the ring clockwise — but each of those nodes is still, individually, "a shard" in this scheme's vocabulary.)
- **Directory-based (MongoDB):** a shard **is a whole replica set** (a group of nodes — typically primary + 2 secondaries), not a single node. "Shard 1" refers to the group, not any one machine in it.
- **Leader-based replication is not a partitioning scheme at all** — it's an orthogonal layer that sits *inside* a shard, regardless of which partitioning scheme decided that shard's existence. It's not a peer of consistent-hashing/directory-based; it answers a completely different question ("how do copies of this shard's data stay in sync") not "which shard owns this key."

**Layer 2 — How is "which shard owns key X" decided:**

- **Consistent hashing:** **computed**, on the fly, every time — `hash(key)`, walk the ring, no lookup table exists anywhere. Ring membership itself is known via gossip (no central authority).
- **Directory-based:** **looked up**, in an explicit table (MongoDB's config servers hold `range → shard`, at chunk granularity ~64-128MB, not per-key). Routers cache this table locally and get invalidated via a version-check-and-refresh mechanism when it changes.

**Layer 3 — Where replication/leadership fits in, per scheme:**

- **Consistent hashing (Cassandra/DynamoDB):** no leader at all, by design. The RF nodes owning a key are equal peers — any of them (via a per-request coordinator) can accept a write. This is the *leaderless* replication model.
- **Directory-based (MongoDB):** each shard (replica set) **does** have a leader — a primary — internally. So MongoDB combines directory-based partitioning *with* leader-based replication *within* each shard. These are two independent design choices that happen to be paired in MongoDB, not a package deal — you could theoretically pair directory-based partitioning with leaderless replication within each group, or consistent hashing with leader-based replication per node-group; MongoDB's specific combination isn't the only valid one, it's just the one MongoDB chose.

**The one-line summary worth memorizing:** *partitioning scheme* answers "which group of machines owns this data" (computed via hashing, or looked up via a directory); *replication model* answers "how do the machines within that group stay in sync" (leaderless peers, or a leader + followers) — and these two questions are answered independently, by independent architectural decisions, even though a given real system (MongoDB, Cassandra) picks one specific combination and ships it as a package.