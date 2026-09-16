## 📑 DynamoDB vs. Cassandra: The Delta Notes
DynamoDB and Cassandra share the same lineage — both descend from Amazon's 2007 Dynamo paper: consistent hashing, leaderless replication, tunable consistency. Everything in the `cassandra/` notes about partition keys, replication, and CAP tradeoffs largely transfers. This page only covers **where they actually diverge** — the parts that would trip you up if an interviewer asked "why not DynamoDB?" after you proposed Cassandra.

------------------------------
## 1. Managed Service vs. Self-Operated Cluster

* **DynamoDB is fully managed**: no nodes to provision, no compaction strategy to pick, no repairs to schedule, no multi-DC topology to configure by hand — AWS handles partitioning, replication (3 AZs within a region by default), and failure recovery internally.
* **Cassandra is self-operated** (or managed via a vendor like DataStax/AWS Keyspaces): you own node sizing, `NetworkTopologyStrategy`, compaction strategy, repair scheduling — everything covered in `tradeoff.md`.
* **The trade-off**: DynamoDB trades operational control for zero-ops convenience. You can't tune compaction strategy, can't pick your own consistency level combinations as freely, and cross-region replication (Global Tables) is a specific managed feature rather than a topology you design yourself.

------------------------------
## 2. Capacity Model: RCU/WCU (or On-Demand) vs. Node Count

* **Cassandra capacity planning** = node count × node capacity, driven by data volume × RF and reads/writes per second (the math in `tradeoff.md` #6).
* **DynamoDB capacity planning** is expressed in **Read Capacity Units (RCU)** and **Write Capacity Units (WCU)**, not nodes:
   * 1 WCU = one write per second for an item up to 1 KB.
   * 1 RCU = one *strongly consistent* read per second for an item up to 4 KB (an *eventually consistent* read costs half an RCU, since it can be served from any replica without a quorum-style read).
   * Or skip capacity planning entirely with **On-Demand mode**, which auto-scales but costs more per request — a direct availability/cost trade-off.
* **Interview translation**: instead of "we need N nodes," the capacity conversation becomes "we need X RCU/WCU, or should the unpredictable traffic pattern push us to On-Demand instead of Provisioned."

------------------------------
## 3. Secondary Indexes Are a Normal Pattern, Not an Anti-Pattern

* In Cassandra (`data_modelling.md` #6), secondary indexes are generally discouraged — they fan a query out to every node.
* DynamoDB's indexes are a core, encouraged part of the modeling toolkit:
   * **Global Secondary Index (GSI)** — a full alternate partition/sort key pair over the whole table, with its own capacity and eventual-consistency-only reads. This is the standard way to support a second access pattern.
   * **Local Secondary Index (LSI)** — same partition key as the base table, alternate sort key; must be created at table-creation time and shares the base table's capacity.
* **Consequence for modeling**: where Cassandra pushes you toward *physically separate denormalized tables* per query pattern, DynamoDB often lets you serve a second access pattern with a GSI on the *same* table instead.

------------------------------
## 4. Native Multi-Item ACID Transactions

* Cassandra's only compare-and-swap mechanism is Lightweight Transactions (Paxos-based), and even those are single-partition and expensive — true multi-row/multi-table transactions aren't a first-class feature (`tradeoff.md` #2).
* DynamoDB has native **`TransactWriteItems`/`TransactGetItems`** — real all-or-nothing ACID transactions across up to 100 items/multiple tables, at roughly double the capacity cost of the equivalent non-transactional operation.
* **When this matters in an interview**: any scenario needing "update these two items together or neither" (e.g. a ledger/balance transfer, an inventory decrement tied to an order) is a much easier native fit for DynamoDB than for Cassandra.

------------------------------
## 5. Single-Table Design

* Because DynamoDB pricing/ops scale per-table in ways that reward fewer tables, and because GSIs let one table serve multiple access patterns, the AWS-native modeling philosophy is **single-table design**: cram every entity type for an application into one table, disambiguated by generic `PK`/`SK` (partition key / sort key) attribute names and prefixed values (e.g. `PK = "USER#123"`, `SK = "ORDER#456"`), with GSIs layered on top for the alternate access patterns.
* This is a deliberate, well-known DynamoDB-specific pattern — it doesn't map onto Cassandra, where the norm is closer to "one physical table per query" (`data_modelling.md` #1).
* Worth knowing by name even if you don't use it: it's often the first thing an AWS-leaning interviewer probes for.

------------------------------
## 6. Item Size Limit

* DynamoDB caps individual items at **400 KB**, hard limit, no exceptions — large blobs (images, documents) must live in S3 with a pointer stored in the item.
* Cassandra has no equivalent hard per-row cap, though very large rows/cells still hurt performance the way an oversized partition does (`data_modelling.md` #4) — it's a soft, practice-driven limit rather than an enforced ceiling.

------------------------------
## 7. Quick-Reference Table

| Concern | Cassandra | DynamoDB |
|---|---|---|
| Operations | Self-managed (or vendor-managed) cluster | Fully managed by AWS |
| Capacity unit | Node count | RCU/WCU or On-Demand |
| Secondary access patterns | New denormalized table (indexes discouraged) | GSI/LSI on the same table |
| Multi-item transactions | Not first-class (LWT is single-partition, expensive) | Native `TransactWriteItems` |
| Modeling philosophy | One table per query | Single-table design (common, not required) |
| Item size limit | No hard cap (soft, perf-driven) | Hard 400 KB cap |
| Multi-region | You configure `NetworkTopologyStrategy` yourself | Managed Global Tables |

------------------------------
## Related Notes
* [../cassandra/tradeoff.md](../cassandra/tradeoff.md) — CAP framing and the original Cassandra-vs-DynamoDB positioning.
* [../cassandra/data_modelling.md](../cassandra/data_modelling.md) — the "one table per query" philosophy this page contrasts against single-table design.
