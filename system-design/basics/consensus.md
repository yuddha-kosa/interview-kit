# Consensus — System Design Notes

> Companion to `partitioning.md` and `replication.md`. Partitioning = spreading different data across nodes. Replication = keeping copies of the same data in sync. Consensus = how a fixed set of nodes agree on a single value (or an ordered sequence of values) even with crashes/slow nodes/partitions, as long as a majority can talk to each other. Underlies leader election (MongoDB, Raft-based systems) and any replicated metadata/config store (etcd, Zookeeper).
>
> Template per topic: (1) Explain, (2) Problem solved, (3) Mechanism, (4) Failure modes, (5) Interview trigger — collapsed per section below since this topic is more mechanism-heavy than enumerative.

---

## 0. The General Problem

**Explain:** How do multiple nodes agree on a single value/ordered sequence, guaranteeing every deciding node decides the *same* thing, and once decided it can't be undone — despite slow nodes, crashes, and unreliable networks, as long as a majority of nodes are alive and reachable.

**Why it's hard:** Not "reaching agreement when healthy" — the hard part is guaranteeing agreement (or safely detecting you can't yet) when messages are delayed, nodes crash mid-decision, or a partition splits the cluster unevenly. Naive "first node to get votes wins" can produce two winners if messages arrive out of order or the network splits unevenly.

**Raft vs. Paxos:** Paxos solves the identical problem, predates Raft by ~15 years, but is notoriously hard to reason about/implement correctly (multiple papers exist just to explain it more clearly — the difficulty is itself famous). Raft was explicitly designed as "Paxos, but understandable" — decomposed into leader election + log replication + safety as separate, teachable pieces. Interview framing: know Paxos as the historical/academic reference; Raft is the practical one actually implemented in CockroachDB, etcd, MongoDB elections, Kafka's KRaft mode. If asked "why did Raft's designers bother when Paxos existed" — answer is understandability without sacrificing correctness.

---

## 1. Raft — Leader Election

**Mechanism:**
- Every node is **Follower**, **Candidate**, or **Leader**. Cluster starts all-Follower.
- Time divided into **terms** — monotonically increasing integers; at most one leader per term. Term increments on *every* new election attempt, whether or not it succeeds.
- Each Follower has a **randomized** election timeout (e.g., 150–300ms). Randomization specifically prevents all nodes timing out simultaneously (which would cause repeated split votes). No heartbeat within the timeout → Follower assumes no leader, increments term, becomes Candidate, votes for itself, sends `RequestVote` to all others.
- Each node votes for **at most one candidate per term**, first-come-first-served, and only if the **candidate's log is at least as up-to-date as its own** (see §1a — this is the safety-critical check).
- Candidate reaching a **majority** of votes (of the cluster's total configured size N — see §3, this is a common point of confusion) becomes Leader for that term, sends periodic heartbeats (empty `AppendEntries`) to reset everyone's timers and suppress new elections.

### 1a. The "log at least as up-to-date" vote check — precise rule

A follower grants its vote only if the candidate's log passes this two-part comparison:
1. Compare the **term of the candidate's last log entry** vs. the follower's own last entry's term. Higher term wins outright.
2. If terms are **equal**, compare **log length** (index of last entry). Longer log wins.

**What "term of the last log entry" means concretely:** every log entry carries both the command and the term during which it was appended (i.e., which leader's tenure wrote it):

```
Index:  1        2        3        4        5
Term:   1        1        2        2        3
Entry:  "x=1"    "y=2"    "x=3"    "z=9"    "x=5"
```

"Candidate's last log entry's term" = look at the last row — here, index 5, term 3.

**Why compare term before raw length:** term reflects legitimacy/recency of leadership tenure, which matters more than entry count. Example: Node A has 5 entries, last at term 3. Node B has 8 entries but got partitioned off right after term 1, so its last entry is still term 1 — those 8 entries could include stale/uncommitted data from before isolation, or writes accepted while B was a minority-side leader that never reached majority commit. Comparing length alone would wrongly favor B (8>5); comparing term first correctly recognizes A as more authoritative. Only when last-entry terms are **equal** does length become the tiebreaker.

**Split vote:** if all (or several) nodes become Candidates in the same term simultaneously (e.g., all timed out near-simultaneously), votes split and nobody reaches majority. Term ends inconclusively. Because timeouts are randomized independently, retries (new term, new election) re-stagger naturally — a full repeat is possible but statistically decreasingly likely each round. Self-resolving, not a stuck state.

---

## 2. Raft — Log Replication

**Mechanism:** Only the leader accepts new writes/operations. Each operation appended to the leader's local log tagged with the current term. Leader sends `AppendEntries` to all followers with the new entry. Once a **majority of the total cluster** (leader included) have persisted it, it's **committed** — durable, safe to apply, and the client is told "success." Leader tracks a `commitIndex` marking how far the log is safely committed. Followers behind (missed entries, just recovered) get targeted catch-up from the leader (leader tracks each follower's progress via response acks — not a full resync).

**Why this generalizes beyond elections:** this is the general building block for "how N machines agree on an ordered list of things that happened" — same primitive underlying a replicated config store (etcd), metadata directory (Zookeeper/config servers), or distributed lock service. Leader election is the special case of this log recording "who's currently allowed to be leader."

---

## 3. Correction: Majority Is Computed Against Fixed Cluster Size N — Not RF, Not "Currently Reachable Nodes"

**This was the core confusion to resolve precisely:**

- **Raft has no separate "RF" the way Cassandra does.** In an N-node Raft cluster, the leader replicates to *every* follower it can reach — there's no designated subset of "3 replica holders" out of a larger total. All N nodes are potential log holders. Majority (for both votes and commits) is always computed against the cluster's **configured total membership N**, never against some smaller replication-factor subset.
- **N does not shrink when a node goes down.** A 5-node cluster always needs 3 for majority, whether all 5 are healthy or only 3 are reachable — a down node doesn't reduce N, it just makes reaching majority harder (or impossible, if too many are down).
- **Cluster membership CAN change**, but only via a deliberate reconfiguration operation (Raft's **joint consensus** protocol) — changing what "majority" means mid-flight is dangerous if done naively, so it's handled as its own careful protocol, not an automatic side effect of a node dying. (Worth knowing this exists; not essential to go deeper on it now.)

### Worked scenario — why committed vs. uncommitted matters for what's "guaranteed"

10-node Raft cluster. Leader appends a new entry, replicates it to 2 followers (3 total including itself), then **crashes** before reaching the other 7. 9 nodes remain: 2 have the entry, 7 don't.

**Was this entry committed?** No — commit requires majority of the *total cluster* (10), i.e., 6. Only 3 ever had it. **The leader never told the client "success"** for it (a correct implementation only acks after majority is reached). Losing this entry on the next election is **expected, correct behavior** — the safety guarantee only covers entries that actually reached true majority.

**What happens in the election:** a candidate from the "7 without the entry" group can validly gather votes from all 7 (their logs are mutually equally up-to-date) — easily clears majority (5 of 9). It wins; its log (lacking the entry) becomes authoritative. The 2 nodes that *had* the entry get told to discard it during catch-up. Correct and safe, precisely because that entry never reached majority.

**Contrast — an entry that WAS committed:** leader crashes after 6 total nodes (itself + 5 followers) had it — a real majority of 10, so it was committed and the client was told "success." 9 nodes remain: 5 have the committed entry, 4 don't. Any candidate needs 5 votes (of the 9 reachable, but majority is still evaluated against the cluster concept of 10 — practically, a candidate must gather votes from enough of the reachable nodes to clear the cluster's majority threshold). **By pigeonhole, since 5 nodes already hold the entry and any winning candidate needs a majority's worth of votes, at least one voting node must already hold the committed entry** — and per the §1a rule, that node will refuse to vote for any candidate whose log doesn't already include it (candidate must be at least as up-to-date). **A candidate lacking the committed entry is mathematically blocked from assembling a winning majority.**

**The corrected one-line summary:** the R+W>N-style overlap logic *does* apply here — but to (nodes required to commit) vs. (nodes required to elect), both drawn from the *same total N*, both requiring majority of that fixed N — not to a separate RF subset. It only guarantees survival for entries that reached true majority before a crash; anything short of that was never promised and is fair game to be discarded on the next election.

---

## 4. Partitions — Can Both Sides Have a Leader? Can Data Go to Both?

**A leader can exist on both sides simultaneously, but only one side can actually commit anything.**

5-node cluster splits 3-2 (old leader can end up on either side):

- **Old leader on the majority side (3 of 5):** still gets majority acks for new writes — fully functional, no issue.
- **Old leader on the minority side (2 of 5):** doesn't know it's partitioned, keeps sending heartbeats, still believes it's leader — but can never get majority ack (2 of 5 isn't enough) for any new write. Clients writing to it get a **hang/timeout**, not a silent false "success." Meanwhile the majority side (3 nodes) stops hearing from it, times out, elects a **new** leader with a **higher term number**.
- **When the partition heals:** the stale minority-side leader receives a heartbeat/vote-request carrying the higher term, recognizes it's outdated, and **steps down automatically** to follower. Any writes it locally accepted but never committed (couldn't reach majority) are discarded/overwritten during catch-up from the new leader's log.

**Direct answer: no, data cannot successfully go to both leaders** — only the majority-side leader can commit; the minority-side leader is a "zombie" that looks like a leader but can't make progress.

**CAP contrast worth holding explicitly:** Raft chooses **consistency over availability** during a partition (minority side goes unavailable rather than risk diverging committed histories). Cassandra chooses the opposite — **availability over consistency** (both sides of a partition keep accepting writes; reconcile divergence afterward via LWW/read-repair/anti-entropy). Same CAP trade-off, opposite choice, now backed by the concrete mechanism on both sides.

---

## 5. Cluster Sizing — Why Odd Numbers

Majority = `⌊N/2⌋ + 1`, computed against fixed configured N (see §3).

- **3-node cluster:** majority = 2. One node down → 2 remain, still majority of 3 → fully functional. Two nodes down → 1 remains, not a majority of 3 → correctly goes unavailable (a lone surviving node must not be allowed to unilaterally decide anything — imagine if it could: a single isolated node could just declare itself leader and diverge from reality).
- **4-node cluster:** majority = `⌊4/2⌋+1 = 3`. Two nodes down → 2 remain, not ≥ 3 → **cannot elect or commit.** Same majority requirement (3) as a 5-node cluster, but tolerates only **1** failure (4−3) vs. 5-node's **2** failures (5−3) — a 4th node bought **zero** extra fault tolerance over 3 nodes for extra cost. This is why production Raft/consensus clusters are essentially always sized odd (3, 5, 7) — an even-sized cluster is strictly dominated by the next odd size down or up.

---

## 6. Why Consensus Is Expensive — Why It's Reserved for Coordination, Not the Data Path

Every committed decision requires a **majority round-trip** — the leader must hear back from `⌊N/2⌋` other nodes before considering anything durable. Real network latency paid **per decision**, not per byte. This is exactly why:
- Cassandra/DynamoDB skip consensus entirely for normal reads/writes — leaderless + quorum reads/writes is cheaper (no election, no log-replication round-trip, just direct replica writes).
- Systems that DO need consensus (etcd, Zookeeper, MongoDB's config servers/replica-set elections, Raft-based leader election generally) reserve it for **metadata and coordination decisions** (who's the leader, what's the current config) — infrequent, low-volume — rather than the actual data path (millions of ops/sec), which uses cheaper mechanisms once the coordination layer has established who's in charge.

## Zookeeper's Role (precise, tying back to earlier sessions)

Zookeeper runs its own consensus protocol internally (**ZAB** — Zookeeper Atomic Broadcast, Paxos-like) among its own small cluster (typically 3–5 nodes), and exposes that as a **coordination service** other systems lean on — leader election, distributed locks, config storage, service discovery — so those systems don't have to implement Raft/Paxos themselves.

- **Kafka historically** depended on Zookeeper for broker metadata and controller (leader) election.
- **Newer Kafka (KRaft mode)** removed that dependency by implementing Raft *internally* — no separate Zookeeper cluster needed. Worth knowing this migration exists; "Kafka needs Zookeeper" is outdated for newer deployments.
- **Cassandra** deliberately uses **neither** Zookeeper nor its own Raft for the data path (leaderless design). Consensus only appears for narrow features like lightweight transactions (`IF NOT EXISTS`), implemented via a Paxos variant specifically because that one operation needs linearizability that gossip+quorum alone can't provide.

---

## Quick self-test (answer before moving on)

1. Why doesn't a down node reduce the cluster's N for majority-counting purposes?
2. In the 10-node scenario (§3), why was it *correct and safe* for the uncommitted entry to be lost, but *guaranteed impossible* for the committed one to be lost?
3. Why compare term before log length when deciding vote eligibility — give the concrete failure case that comparing length-only would cause.
4. During a partition, why can a minority-side "leader" not simply keep accepting writes and reconcile later, the way Cassandra would?
5. Why does a 4-node cluster provide zero fault-tolerance benefit over a 3-node cluster?

## Open threads / to revisit
- Joint consensus (safe cluster membership reconfiguration) — flagged but not gone deep on.
- Next per agreed ordering: **data modeling / modeling without joins**, then **elastic cluster scaling**, then end-to-end system design on a couple of real distributed databases.
- Still open from partitioning.md: enterprise-ID compound-key fix — range-based or directory-based mentally?
