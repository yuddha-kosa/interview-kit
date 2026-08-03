Cassandra uses a "Log-Structured Merge-Tree" (LSM Tree) architecture for writing data. It is highly optimized for writes because it converts random writes into fast, sequential memory operations, delaying disk writes for later. [1, 2, 3, 4] 
Here is the exact step-by-step path your data takes during a write operation, and exactly where SSTables fit into the picture. [5] 
------------------------------
## The Cassandra Write Path (Step-by-Step)
When your application sends a write request to a Cassandra node, the data is written to two places simultaneously in memory and on disk: [6, 7] 

                  ┌────────────────────────┐
                  │   Write Request (CQL)  │
                  └───────────┬────────────┘
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
    ┌────────────────────┐        ┌────────────────────┐
    │  CommitLog (Disk)  │        │   Memtable (RAM)   │
    │  (Sequential append│        │ (In-memory buffer) │
    │   for recovery)    │        │                    │
    └────────────────────┘        └──────────┬─────────┘
                                             │
                                             │ (When Memtable fills up)
                                             ▼
                                  ┌────────────────────┐
                                  │   SSTable (Disk)   │
                                  │(Immutable file, sorted)
                                  └────────────────────┘

## 1. The CommitLog (Disk - Sequential Write) [8] 

* What it is: A simple, append-only log file stored on disk.
* Why it exists: For crash recovery. Because RAM is volatile, if the server loses power, any data stored only in memory would be lost.
* Performance: Appending to the end of a file is incredibly fast for hard drives and SSDs because it requires no random searching. [9, 10, 11, 12, 13] 

## 2. The Memtable (RAM - Sorted in Memory)

* What it is: A write-back cache in RAM that stores data for a specific table. [14, 15] 
* How it works: The incoming data is stored in the Memtable, where it is automatically sorted by its partition key token and clustering keys. [16, 17] 
* The "Success" Signal: Once the data is successfully written to both the CommitLog and the Memtable, Cassandra immediately sends a Success acknowledgement back to your application. The write is complete, taking only microseconds. [18, 19] 

------------------------------
## Where Do SSTables Come into the Picture?
An SSTable (Sorted String Table) is the final, permanent home for your data on disk. It is introduced during a process called Flushing. [20, 21, 22, 23, 24] 
## 3. The Memtable Flush
Memtables cannot grow in RAM forever. When a Memtable reaches its size limit (or the CommitLog gets too full), Cassandra triggers a Flush. [25, 26, 27] 

* Cassandra takes the sorted data from the Memtable in RAM and writes it out to disk as a brand new file.
* This file on disk is the SSTable.
* Once the SSTable is safely written to disk, the old Memtable is cleared from memory, and its corresponding entries in the CommitLog are safely deleted. [28, 29, 30, 31, 32] 

## Key Characteristics of SSTables

* Immutable: Once an SSTable file is written to disk, it is never altered. Cassandra never performs an "in-place" update or deletion. [33, 34, 35] 
* What about Updates? If you update a user's name, Cassandra simply writes a new entry with the new name to a new SSTable. The old name stays in the old SSTable. [36, 37] 
* What about Deletions? If you delete a user, Cassandra writes a special marker called a Tombstone to a new SSTable, signaling that the data is deleted. [38, 39, 40] 

------------------------------
## The Problem: Too Many SSTables (Compaction)
Because every flush creates a new SSTable, a single table might eventually have dozens of SSTable files on disk. If your application tries to read a user's data, Cassandra might have to look inside 10 different SSTables to piece together the latest updates and handle tombstones. [41, 42] 
To fix this, Cassandra runs a background process called Compaction: [43, 44, 45] 

   1. It reads multiple old SSTables simultaneously.
   2. It merges their data, keeping only the newest updates and discarding deleted data (tombstones).
   3. It writes out one clean, optimized, consolidated new SSTable.
   4. It deletes the old, redundant SSTable files. [46, 47, 48, 49, 50] 

## Summary
Cassandra writes instantly to a CommitLog (disk) and Memtable (RAM). When the memory fills up, it flushes that data to disk as an SSTable. SSTables are immutable files sorted by key, which are periodically merged together via Compaction to keep reads fast. [51, 52, 53, 54, 55] 
Would you like to explore how Cassandra performs a Read operation using these SSTables (via Bloom Filters and Key Caches), or are you curious about how Compaction strategies affect system performance?
