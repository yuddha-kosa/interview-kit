## 📑 PostgreSQL Storage & MVCC Architecture: Complete Study Notes
This comprehensive summary captures the exact mechanical behavior of how PostgreSQL manages, structures, and isolates data at the storage layer.
------------------------------
## 1. The Core Architecture: Heap vs. B-Tree
Unlike databases that bake data directly into index leaves, Postgres keeps data and indexes completely decoupled in separate physical files on disk. [1] 

* The Heap File (The Data): The primary file storing raw table records (called Tuples). It is a collection of unstructured, fixed-size 8KB pages. Tuples are unsorted and dumped into whichever page has available space. [2, 3, 4, 5] 
* The B-Tree File (The Index): A completely separate file built for every individual index on a table. Leaves do not hold raw data; they store the indexed key and a Tuple ID (TID) pointer pointing to a physical address: (Page Number, Offset Number) inside the Heap. [6, 7, 8, 9] 
* The OID Mapping (pg_class): Postgres tracks the location of these trees and heaps using a system catalog table. Every table/index gets a unique tracking number (Object Identifier). The physical disk file is literally named after this ID (e.g., /base/13542/16384). [10, 11, 12] 

------------------------------
## 2. The Write Path & WAL Layer
To maximize performance, Postgres converts slow, random disk updates into fast, sequential memory writes using caching and a transaction log:

   1. Shared Buffers (RAM): Incoming changes modify the Heap and B-Tree pages only inside memory first. These are called Dirty Pages. [13] 
   2. Write-Ahead Log / WAL (Disk Append): Before acknowledging success to your application, Postgres appends a brief architectural log of the transaction to the sequential WAL file on disk. This guarantees durability if the server crashes before RAM is flushed. [14, 15] 
   3. The Checkpoint: A background process periodically flushes all dirty pages from the RAM Shared Buffers out to their permanent homes inside the physical Heap and B-Tree files on disk. [16, 17, 18] 

------------------------------
## 3. MVCC & Row Versioning in the Heap
Postgres enforces Multi-Version Concurrency Control (MVCC) to allow transactions to read and write simultaneously without locking tables. [19, 20] 

* The Metadata Flags: Every tuple inside an 8KB heap page contains internal tracking headers:
* xmin: The Transaction ID that inserted this specific version.
   * xmax: The Transaction ID that updated or deleted this specific version (0 if still active). [21, 22, 23, 24] 
* The Anatomy of an UPDATE:
* The old tuple is left completely intact on disk. Its xmax is updated to the current transaction ID to signify it is dead to future transactions.
   * A brand-new version of the tuple is appended to an open space in an 8KB page with its xmin set to the current transaction ID. [25, 26, 27, 28] 

------------------------------
## 4. The Impact on B-Tree Indexes
Because updates duplicate and move rows within the Heap file, the index architecture suffers severe write side effects:

* Index Multiplication: Every time a row gets a new version in the heap, all indexes on that table must insert a new pointer to the new location, even if the indexed column didn't change. [29] 
* Dead Pointers in the B-Tree: Old index keys (e.g., Key: "Old Phone" -> Points to Old Tuple) remain inside the B-Tree file. They cannot be instantly deleted because ongoing, older transactions might still need them to construct a historically accurate view of the data.

------------------------------
## 5. How Queries Pick the Right Version
If an index search returns multiple pointers for the same logical record, Postgres resolves it using Metadata Filtering:

   1. The query executor follows the B-Tree pointers and pulls all matching tuples from the Heap pages into RAM.
   2. It evaluates the tuple's xmin and xmax metadata against the query's own Snapshot (the list of active transaction IDs when the query started).
   3. The Filtration: It immediately discards any tuple that is marked as dead (xmax) or uncommitted to its specific snapshot, processing and returning exactly one valid version to the application. [30] 

------------------------------
## 6. Table Bloat & The Remediation Layer
Accumulating dead tuples in the Heap and dead pointers in the B-Tree leads to Bloat, which wastes disk space and slows down page scanning. Postgres resolves this via two mechanisms: [31, 32] 

* LP_DEAD Flagging (Micro-Cleanup): Regular index reads that discover dead tuples will flag the corresponding B-Tree leaf as LP_DEAD. Future write operations on that specific 8KB index page will proactively overwrite those slots.
* The VACUUM Process (Macro-Cleanup): A global background worker that executes a strict two-pass routine:
* Pass 1: Scans the Heap file to assemble a master list of all dead tuple addresses.
   * Pass 2: Scans the B-Tree index files to permanently purge and unlink any keys pointing to those dead addresses, reclaiming the empty space for future inserts. [33, 34] 

Would you like to save these notes as they are, or should we add a final cheat-sheet table summarizing the direct technical differences between Cassandra and Postgres side-by-side?
