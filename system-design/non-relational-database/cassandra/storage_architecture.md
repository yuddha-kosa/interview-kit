## 📑 Apache Cassandra Storage Architecture: Complete Study Notes
This comprehensive summary captures the complete mechanical behavior of how Apache Cassandra manages, structures, and writes data from your application layer down to the physical disk.
------------------------------
## 1. The Architectural Naming Misnomer

* Wide-Column / Column-Family Store: This is the accurate description of modern Cassandra. It is not a true columnar database (like ClickHouse or Snowflake).
* Row-Oriented Under the Hood: While it mimics schema flexibility, Cassandra physically organizes and stores data on disk by partitions (rows), not by standalone columns.

------------------------------
## 2. The Multi-Node & Coordinator Layer

* The Token Ring: Cassandra uses Consistent Hashing. It hashes your Partition Key into a 64-bit integer called a Token. Token ranges are divided among all nodes in the cluster.
* The Coordinator Node: Any node that receives a query from your application acts as the Coordinator.
* If it owns the token, it reads locally.
   * If it does not, it forwards the request across the network to the correct replica nodes.
* Global Scan Hazard (SELECT *): Executing a full table scan without a WHERE clause forces the Coordinator to broadcast requests to every single node in the cluster. This bypasses indexes, risks server JVM heap exhaustion (OOM), and crashes production systems.

------------------------------
## 3. The Write Path (LSM-Tree Engine)
Cassandra converts random writes into high-speed sequential memory operations using an LSM (Log-Structured Merge) Tree layout:

   1. CommitLog (Disk): An append-only sequential file used strictly for crash recovery. Writes are incredibly fast because the disk head never jumps around.
   2. Memtable (RAM): A write-back memory buffer where data is automatically sorted by its partition token and clustering keys.
   3. The Flush: When the Memtable fills up, Cassandra freezes it and writes its contents out to disk as a brand new, permanent SSTable file.

------------------------------
## 4. The Anatomy of an SSTable
An SSTable (Sorted String Table) is the final, permanent file structure on disk.

* Immutability: Once written to disk, an SSTable is never modified or updated in place.
* Updates & Deletions: Updates simply write a newer cell timestamp to a newer SSTable. Deletions write a special marker called a Tombstone to a new SSTable.
* Isolation: The file system enforces strict nesting isolation: /data/[Keyspace]/[Table-UUID]/mc-X-big-Data.db. SSTables can never be shared across different keyspaces.
* Compaction: A background process that reads multiple old SSTables, merges their data, discards overwritten fields/tombstones, writes one consolidated new SSTable, and deletes the old ones to keep reads fast.

------------------------------
## 5. Physical Mapping: Partitions vs. CQL Rows
There is a fundamental difference between how data looks to your code versus how it looks to the hard drive:
## The Mathematical Layout Rules

   1. One SSTable houses many sorted partitions. Partitions sit side-by-side inside the file, ordered by their token hash.
   2. One Partition can be fragmented across multiple SSTables. Over time, pieces of a single partition's history live in separate files until Compaction unifies them.
   3. The Cell Multiplying Rule: For every regular column populated in a CQL row, Cassandra writes exactly one independent cell on disk. Empty columns create zero cells and consume $0$ bytes of storage.

## Visualizing the Disk Flat Tape
Cassandra uses a Row Marker (a structural metadata tag containing the clustering key value) to mark where a logical row begins, followed immediately by its regular columns.
Given a table with 2 regular columns (action_name, device) and 5 distinct data entries grouped by a clustering key (action_time) under User_A:

* Your Application Sees (Logical CQL Rows): 5 neat tabular rows inside a grid.
* The Physical Storage Disk Sees (One Wide Row Partition): 5 Row Markers and 10 Column Cells laid out flatly, back-to-back, pre-sorted by the timeline:

💾 [PARTITION HEADER: User_A] 
      │
      ├── 🏷️ [Row Marker: 10:00 AM] ── (Holds clustering key value)
      │     ├── 📄 [Column: action_name] = "Login"
      │     └── 📄 [Column: device]      = "Mobile"
      │
      ├── 🏷️ [Row Marker: 10:05 AM]
      │     ├── 📄 [Column: action_name] = "Click"
      │     └── 📄 [Column: device]      = "Mobile"

Because of this sequential, physical proximity layout, a query utilizing LIMIT 3 can jump straight to the partition header using companion Index and Bloom Filter files, read exactly 3 Row Markers linearly, and safely stop reading the disk immediately.
------------------------------
## 6. Strong Consistency Formula
Because replica nodes can fall out of sync over time, you can enforce strong consistency dynamically at the query layer using this rule:
$$\text{Write Consistency Level (W)} + \text{Read Consistency Level (R)} > \text{Replication Factor (RF)}$$ 

* Using Quorum (majority) for both reads and writes ensures that the Coordinator node will always compare timestamps from multiple replicas, serve the newest cell, and silently fix out-of-date nodes via a background Read Repair.

Would you like to save these notes as they are, or should we append a section on how to choose an optimal Partition Key vs. Clustering Key based on this physical storage design?
