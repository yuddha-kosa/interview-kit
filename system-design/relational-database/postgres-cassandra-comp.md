You have asked an incredible series of deep architectural questions. Let's break down the physical reality of PostgreSQL's storage engine and contrast it directly with how Cassandra operates.
First, a critical correction to align with your mental model: PostgreSQL does not store data in the leaves of a B-Tree. That is how MySQL (InnoDB) or SQL Server work. Postgres does something completely different using Heaps. [1, 2, 3] 
Here is exactly how the Heap, B-Trees, and the WAL interact on disk.
------------------------------
## 1. What are the "Heap" and the "B-Tree" in Postgres?
In Postgres, data and indexes are kept in completely separate physical files on disk. [4, 5, 6] 

                       ┌────────────────────────┐
                       │  Postgres Table Files  │
                       └───────────┬────────────┘
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐                 ┌─────────────────────────────────┐
│       THE HEAP FILE             │                 │       THE B-TREE FILE           │
│  (Stores the Actual Data Rows)  │                 │     (Stores the Indexes)        │
│                                 │                 │                                 │
│ ┌─────────────────────────────┐ │                 │ ┌─────────────────────────────┐ │
│ │ Page 1 (8KB)                │ │                 │ │ Root Node Page (8KB)        │ │
│ │  - Tuple 1 ("Alice", 30)   │ │                 │ └──────────────┬──────────────┘ │
│ │  - Tuple 2 ("Bob", 25)     │◄┼─────────────────┼────────────────┤                 │
│ └─────────────────────────────┘ │ (Points to Tuple│                ▼                 │
│ ┌─────────────────────────────┐ │  via ItemPointer)┌─────────────────────────────┐ │
│ │ Page 2 (8KB)                │ │                 │ │ Leaf Node Page (8KB)        │ │
│ │  - Tuple 3 ("Charlie", 35)  │ │                 │ │  - Key: "Bob" -> (Page 1,  │ │
│ └─────────────────────────────┘ │                 │ │                  Offset 2) │ │
└─────────────────────────────────┘                 └─────────────────────────────────┘

## The Heap File (The Data)
The Heap is the primary file that holds your raw table data. [7] 

* It is a collection of unstructured, fixed-size 8KB Pages.
* When you run INSERT, Postgres finds any 8KB page in the heap file that has empty space and dumps the row (called a Tuple) right into it.
* Rows are not sorted in the heap. They are placed wherever they fit. [8, 9, 10, 11, 12] 

## The B-Tree File (The Index)
If you create an index on name, Postgres creates a completely separate file containing a B-Tree. [13] 

* Every node/page in this B-Tree is also 8KB.
* As you correctly calculated, it uses a branching factor (e.g., 100 entries per page) resulting in a $\log_{100}(N)$ traversal depth.
* The Leaves: The leaf nodes of a Postgres B-Tree do not contain the actual row data. Instead, they contain a key and a Tuple ID (TID) (also called an Item Pointer), which looks like (Page Number, Offset Number). [14, 15, 16, 17, 18] 

To read a row via an index, Postgres traverses the B-Tree, grabs the TID (Page 5, Row 2) from the leaf node, and then jumps straight to Page 5, Row 2 inside the Heap file. [19, 20] 
------------------------------
## 2. Is there a B-Tree per table? How does Postgres find the Root?

* Is there a tree per table? No, there is one Heap file per table, and one B-Tree file for every individual index you create on that table. If a table has 3 indexes, it has 1 Heap file and 3 separate B-Tree files. [21, 22, 23, 24] 
* How does it find the Root/Table? Postgres maintains an internal master system catalog table called pg_class.
* Every table and index in your database is assigned a unique tracking number called an OID (Object Identifier).
   * The physical file on your hard drive is literally named after this OID (e.g., a file named /base/13542/16384).
   * When you run SELECT * FROM users, Postgres looks up users in pg_class, grabs its OID, opens that exact file identifier on disk, and reads it block by block. [25, 26, 27, 28] 

------------------------------
## 3. When does the WAL (Write-Ahead Log) come into the picture?
Modifying B-Trees and Heap pages directly on disk for every single transaction is incredibly slow because it requires random I/O (hopping around different files). To make writes fast, Postgres uses the WAL and memory caching: [29, 30] 

   1. In-Memory Modification: When you write data, Postgres modifies the Heap page and B-Tree page only inside RAM (a memory cache area called Shared Buffers). These modified pages in RAM are now called "dirty pages." [31, 32] 
   2. The Append: Before sending a "Success" signal back to your application, Postgres writes a brief architectural description of the change to the WAL file on disk. The WAL is a sequential, append-only log. [33, 34] 
   3. The Guarantee: Once the WAL is safely flushed to disk, the transaction is safe. If the server loses power right now, the data in RAM is lost, but during reboot, Postgres will read the sequential WAL file and replay the changes back into the Heap and B-Tree files. [35, 36, 37] 
   4. The Checkpoint: Periodically (e.g., every 5 minutes), a background process called the Checkpointer takes all the dirty pages from RAM and flushes them to their permanent home in the physical Heap and B-Tree files on disk. [38, 39, 40, 41] 

------------------------------
## 4. Cassandra Bloom Filters vs. Postgres Mechanisms
You noted that Cassandra uses Bloom Filters because one partition's data can be fragmented across 10 different SSTables.
Postgres does not need Bloom Filters for core table lookups because data is never fragmented across files the way it is in Cassandra. In Postgres, a row lives in exactly one place inside the Heap file. [42] 

| Mechanism | Apache Cassandra 🚀 | PostgreSQL 🐘 |
|---|---|---|
| Data Location | Fragmented across multiple chronological SSTables. | Located in exactly one specific page inside the Heap. |
| How it finds data | Checks Bloom Filters of all SSTables to see which files might have the data, then checks the partition index of those files. | Looks up the key in the B-Tree Index file to fetch the exact pointer (Page, Row ID), then goes directly to that page in the Heap. |
| Memory Map | Key Cache / Row Cache maps partition keys to SSTable file locations. | Buffer Pool (Shared Buffers) caches the exact 8KB blocks of the Heap/Index files in RAM. |

## Does Postgres ever use Bloom Filters?
Yes, but only dynamically in memory during complex queries! If you perform a massive JOIN between two huge tables, Postgres will temporarily construct a Bloom filter in RAM to instantly discard rows that don't match the join condition before scanning the second table, but it is not used as a permanent disk-routing map like it is in Cassandra.
Does understanding the split between the Heap (data rows) and the B-Tree (pointers to rows) clarify why Postgres updates carry more overhead than Cassandra? We can explore how MVCC row versioning impacts this Heap setup next if you'd like.
