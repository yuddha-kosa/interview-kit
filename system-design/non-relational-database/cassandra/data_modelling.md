## 📑 Apache Cassandra Data Modeling: Complete Study Notes
Cassandra data modeling flips the relational mindset: you design tables around your **queries**, not around your entities. There are no joins and no cheap ad-hoc filtering, so the query patterns have to be known up front and baked into the table design.

------------------------------
## 1. Query-First Design ("Query-Driven Modeling")

* Start from "what will my application ask for?", not "what are my entities?".
* Because there are no joins, each distinct read pattern typically needs its own table, purpose-built so that query is a single-partition read.
* It's common to store the same data multiple times, shaped differently, for different queries — e.g. `orders_by_user` and `orders_by_status` as separate tables holding overlapping data.
* Denormalization is the default here, not a shortcut you reach for under pressure.

------------------------------
## 2. Partition Key = Your Query's WHERE Clause

* Whatever columns you need equality predicates on to fetch a result — that's your partition key.
* The partition key is hashed into a Token that decides which node owns the row, and it's the boundary that physically groups data together on disk (see `storage_architecture.md`).
* If a query can't supply the full partition key, Cassandra can't route it to one node efficiently — you'd need `ALLOW FILTERING` (bad idea at scale) or a secondary index.

------------------------------
## 3. Two Competing Partition-Key Goals: Even Spread vs. Co-location

* You want partitions small and evenly distributed across nodes (avoid hotspots).
* You also want data that's read together to live together — that's the whole point of a partition.
* Composite partition keys like `(user_id, month)` are the usual fix: they spread what would otherwise be one giant unbounded partition (e.g. `user_id` alone, for a chatty user with years of activity) into many bounded ones.

------------------------------
## 4. Unbounded / "Wide" Partitions Are the Classic Anti-Pattern

* Sensor data, activity logs, chat history — anything that grows forever under one partition key eventually blows past the recommended partition size.
* Rule of thumb: keep partitions under ~100MB / ~100k cells.
* Time-bucketing the partition key (per day/month) is the standard fix.
* Changing a partition key later means a full backfill into a new table, so this needs to be right up front.

------------------------------
## 5. Clustering Key = Your Query's ORDER BY / Range

* Determines on-disk sort order within a partition.
* `WHERE` range predicates (`>`, `<`, `BETWEEN`) and `ORDER BY` only work along the clustering columns.
* Example: an `action_time` clustering key sorts activity chronologically inside a `User_A` partition for free, with no extra sort step at read time.

------------------------------
## 6. Secondary Indexes Are Usually a Smell

* A secondary index on a Cassandra table fans a query out to **every node** (the index is local per-node, not global), which defeats the whole point of partition routing.
* Fine for low-cardinality, low-traffic lookups in dev.
* In production, prefer a second table maintained at write time instead.

------------------------------
## 7. Materialized Views Exist but Are Fragile

* Cassandra can auto-maintain a denormalized view for you.
* MVs have a history of consistency bugs in production Cassandra.
* Most teams still hand-maintain duplicate tables via batched writes at the application layer rather than trust MVs.

------------------------------
## 8. Model Around Avoiding Tombstones

* Deletes (and expiring TTL'd data, and updates to `list` collections) write tombstone markers.
* A read that has to skim over a lot of tombstones to find live data degrades badly — Cassandra will even refuse a read past a tombstone-count threshold.
* Prefer patterns where "deleting old data" = dropping an entire time-bucketed partition/table, rather than deleting rows one at a time.

------------------------------
## 9. It's Optimized for Writes, Not Reads

* Per the LSM-tree write path, writes are cheap (sequential, buffered in RAM) and reads are the expensive, careful part.
* The modeling bias: do the expensive denormalization work at write time (write to N tables), so every read is a single cheap partition lookup.

------------------------------
## Related Notes
* [storage_architecture.md](storage_architecture.md) — physical SSTable/Memtable layout, partition vs. clustering key mechanics.
* [read.md](read.md) — how a read request finds the right replica node.
* [how_data_is_written.md](how_data_is_written.md) — the write path in detail.
* [tradeoff.md](tradeoff.md) — why Cassandra vs. alternatives, multi-DC/failure reasoning, and capacity math for the interview.
