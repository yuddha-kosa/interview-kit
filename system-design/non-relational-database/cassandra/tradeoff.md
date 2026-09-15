## 📑 Cassandra Trade-offs: Staff-Level System Design Notes
Everything in `storage_architecture.md`, `read.md`, and `data_modelling.md` covers *how* Cassandra works. This page covers the layer a staff-level interview actually probes: *why choose it, how it fails, and how to turn requirements into numbers.*

------------------------------
## 1. Why Cassandra vs. the Alternatives (CAP Framing)

* **CAP positioning**: Cassandra is an AP system by default — it stays available and partition-tolerant, sacrificing strict consistency during a network partition. But consistency isn't fixed; it's **tunable per query** via the R/W/N formula, so a single QUORUM read/write can behave close to CP for that one operation, at a latency cost.
* **vs. DynamoDB**: same Dynamo-paper lineage (leaderless, consistent hashing, tunable consistency), but DynamoDB is fully managed/serverless with a different ops and pricing model, plus native ACID transactions. Cassandra gives you more control over topology and multi-DC placement, at the cost of running it yourself.
* **vs. HBase**: HBase is a CP system (built on HDFS + a master/region-server architecture, coordinated via ZooKeeper) — strongly consistent, but write availability suffers during a partition since it isn't leaderless. Pick HBase when strong consistency matters more than write availability; pick Cassandra for the opposite.
* **vs. sharded Postgres/MySQL**: relational gives you joins, ad-hoc queries, and real transactions, but manual sharding and resharding at scale is operationally painful. Cassandra gives you horizontal scaling and active-active multi-DC replication built in, at the cost of no joins and no cheap ad-hoc queries.
* **Pick Cassandra when**: write-heavy, need availability across regions, query patterns are known and stable in advance, and you're willing to denormalize.
* **Avoid Cassandra when**: you need complex ad-hoc queries/joins/aggregations (pair it with a search index or warehouse instead), you need strong consistency with minimal per-query tuning, query patterns are still evolving, or the dataset is small enough that a distributed system's operational overhead isn't worth it.

------------------------------
## 2. Tunable Consistency as a Lever

* **The formula**: $W + R > N$ guarantees every read sees the latest write (recap from `storage_architecture.md`).
* **Common levels**: `ONE` (fastest, weakest), `QUORUM` (majority of all replicas), `LOCAL_QUORUM` (majority within the local DC only), `EACH_QUORUM` (majority in *every* DC), `ALL` (strongest, least available).
* **The trade curve**: every step toward stronger consistency costs latency and availability — a `QUORUM` write blocks until a majority of replicas ack, so it fails harder during a partition than `ONE` does.
* **This still isn't linearizability**: `QUORUM` resolves conflicting *concurrent* writes via last-write-wins-by-timestamp, not true compare-and-swap. For an actual uniqueness constraint (e.g. "claim this username exactly once"), you need a **Lightweight Transaction** (Paxos-based CAS) — correct, but expensive (multiple round trips), so reserve it for genuinely rare, contended operations, not general writes.

------------------------------
## 3. Multi-DC / Multi-Region Replication

* **`NetworkTopologyStrategy`**: replication factor is set *per datacenter*, e.g. `{'dc1': 3, 'dc2': 3}` — each DC holds a full independent replica set, enabling active-active writes in every region.
* **`LOCAL_QUORUM` is the common default** for cross-region systems: the coordinator only waits for a quorum of *local*-DC replicas, keeping the hot path off the cross-region network round trip. The trade-off: a successful local ack doesn't guarantee the other DC has the data yet — that copy arrives asynchronously.
* **Rack awareness**: within a DC, `NetworkTopologyStrategy` also spreads replicas across racks, so a single rack failure can't take out every replica of a partition.
* **Failure detection**: nodes track each other's liveness via the Gossip protocol using a **Phi Accrual failure detector** — a probabilistic suspicion score rather than a simple heartbeat timeout, which adapts to normal network jitter instead of false-alarming on it.
* **Hinted Handoff**: if a replica is briefly unreachable when a write arrives, the coordinator stores a replayable "hint" and replays it once that node returns — this bridges short outages without a full repair. Hints expire after a window (default ~3 hours); beyond that, only Anti-Entropy Repair can reconcile the gap.
* **Anti-Entropy Repair (`nodetool repair`)**: a periodic, deliberate process that compares Merkle tree hashes of data ranges between replicas and reconciles differences. This has to run regularly, inside the **GC grace period** — otherwise a tombstone can expire and be garbage-collected on one replica while a stale, un-repaired replica still has the "deleted" data, which can resurrect it on a later read ("zombie data").

------------------------------
## 4. Compaction Strategy Choice

* **Size-Tiered (STCS)** — the default. Merges similarly-sized SSTables together; good general-purpose choice for write-heavy workloads, but a large compaction can temporarily need up to ~2x the disk space of the data being compacted.
* **Leveled (LCS)** — organizes SSTables into fixed-size levels, minimizing how many SSTables a single read has to touch. Good for read-heavy workloads, at the cost of significantly more background I/O on writes.
* **Time-Window (TWCS)** — purpose-built for time-series data written with TTLs. Groups SSTables by time bucket, so an entire expired window can be dropped as a whole file once its TTL passes — sidestepping the tombstone-accumulation problem from `data_modelling.md` #8 entirely, instead of relying on per-row tombstones and compaction to clean them up.
* **Guidance**: TWCS for time-series + TTL data, LCS for read-heavy workloads that can absorb the extra write I/O, STCS as the safe generalist default otherwise.

------------------------------
## 5. Hot Partition Mitigation in Practice

* **Symptoms**: one node consistently hotter (CPU/disk/latency) than its peers, with spikes traceable to specific keys.
* **Causes**: a skewed partition key — a celebrity/whale user, a viral product ID, a single "global counter" row — or a time-series key that isn't bucketed finely enough.
* **Mitigations**:
   * **Salting**: append a random or hashed suffix to the partition key to fan a hot key out across many physical partitions, then merge results at the application layer.
   * **Isolate the outlier**: route known-hot entities to a dedicated table or handling path instead of letting them share infrastructure with the normal-case data.
   * **Cache in front**: absorb read hot spots with an application-level or Redis cache rather than hitting the hot partition on every read.
* **Vnodes**: each physical node owns many small, non-contiguous token ranges instead of one large contiguous range. This spreads a hot range's impact across many owning nodes and speeds up rebalancing after a node join/leave, versus a single big range moving as one unit.

------------------------------
## 6. Applying This in an Interview: Capacity Math

Don't just say "we'll use Cassandra" — show the requirements turn into concrete numbers.

* **Storage**: logical data volume × replication factor = raw stored data. E.g. 10 TB logical data at RF=3 → 30 TB raw. If each node comfortably holds ~1–2 TB of compacted data (keeping disk utilization under ~50–60% to leave headroom for compaction overhead), that's roughly 20–30 nodes *before* accounting for growth.
* **Multi-DC multiplies this again**: with `NetworkTopologyStrategy` replicating a full RF-sized copy into each DC, a 2-DC active-active deployment doubles the total storage footprint versus a single-DC estimate — a detail that's easy to forget and worth calling out explicitly.
* **Throughput**: replication multiplies write fan-out — a logical write at RF=3 is really 3 physical writes across replicas. So per-node write throughput ≈ (total writes/sec × RF) ÷ node count. Reads at `LOCAL_QUORUM` similarly touch a subset of local replicas per request, not just one.
* **The point of doing this out loud in an interview**: it demonstrates you can translate "we expect X writes/sec and Y TB of data, need Z 9s of availability" into a concrete RF, consistency level, and node count — and justify each choice against the system's actual read/write ratio and availability bar, rather than treating Cassandra as a black box.

------------------------------
## 7. The Interview Crib Summary

> "We'd use Cassandra because we need AP behavior, active-active multi-DC availability, high write throughput, and our query patterns are known and stable up front. We'd use `NetworkTopologyStrategy` with RF=3 per DC and `LOCAL_QUORUM` for the read/write balance across regions, TWCS if this is time-series data with a TTL, and salted partition keys if there's a hot-key risk like a viral post or a celebrity user. In exchange, we're giving up ad-hoc queries and multi-row transactions — which we'd cover with [a search index / a warehouse / denormalized tables], not Cassandra itself."

------------------------------
## Related Notes
* [storage_architecture.md](storage_architecture.md) — physical SSTable/Memtable layout, the $W + R > N$ formula.
* [read.md](read.md) — token ring routing and why a local read still touches multiple SSTables.
* [data_modelling.md](data_modelling.md) — partition/clustering key design, tombstones, why writes are cheaper than reads.
