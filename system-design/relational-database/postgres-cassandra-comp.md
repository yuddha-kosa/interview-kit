# PostgreSQL vs Cassandra: Storage Internals

PostgreSQL does not store data in the leaves of a B-Tree — that's how MySQL (InnoDB) or SQL Server work. Postgres uses a **Heap** instead. Here's exactly how the Heap, B-Tree, and WAL interact on disk, and how that differs from Cassandra's SSTable-based design.

---

## 1. The Heap and the B-Tree

In Postgres, data and indexes are kept in completely separate physical files on disk.

```text
Postgres Table
 │
 ├── Heap File (data)
 │     Page 1: Tuple("Alice", 30), Tuple("Bob", 25)
 │     Page 2: Tuple("Charlie", 35)
 │
 └── B-Tree File (index on `name`)
       Root Page
         └── Leaf Page: "Bob" -> (Page 1, Offset 2)
```

### The Heap file (the data)

The Heap is the primary file that holds your raw table data.

- It is a collection of unstructured, fixed-size 8KB pages.
- When you run `INSERT`, Postgres finds any 8KB page in the heap file that has empty space and dumps the row (called a **Tuple**) right into it.
- Rows are not sorted in the heap — they are placed wherever they fit.

### The B-Tree file (the index)

If you create an index on `name`, Postgres creates a completely separate file containing a B-Tree.

- Every node/page in this B-Tree is also 8KB.
- It uses a branching factor (e.g., 100 entries per page), resulting in a `log₁₀₀(N)` traversal depth.
- **The leaves**: leaf nodes of a Postgres B-Tree do not contain the actual row data. Instead, they contain a key and a **Tuple ID (TID)** — also called an Item Pointer — which looks like `(Page Number, Offset Number)`.

To read a row via an index, Postgres traverses the B-Tree, grabs the TID (e.g., `Page 5, Offset 2`) from the leaf node, and jumps straight to that page in the Heap file.

---

## 2. Is there a B-Tree per table? How does Postgres find the root?

- **Is there one tree per table?** No — there is one Heap file per table, and one B-Tree file for *every* index on that table. A table with 3 indexes has 1 Heap file and 3 separate B-Tree files.
- **How does it find the root/table?** Postgres maintains an internal system catalog table called `pg_class`.
  - Every table and index is assigned a unique tracking number called an **OID** (Object Identifier).
  - The physical file on disk is literally named after this OID (e.g., `/base/13542/16384`).
  - When you run `SELECT * FROM users`, Postgres looks up `users` in `pg_class`, grabs its OID, opens that exact file, and reads it block by block.

---

## 3. When does the WAL (Write-Ahead Log) come into play?

Modifying B-Tree and Heap pages directly on disk for every transaction is slow because it requires random I/O. To make writes fast, Postgres uses the WAL and memory caching:

1. **In-memory modification** — Postgres modifies the Heap page and B-Tree page only inside RAM (`shared_buffers`). These modified pages are now "dirty pages."
2. **The append** — before acknowledging success, Postgres appends a brief description of the change to the WAL file on disk. The WAL is a sequential, append-only log.
3. **The guarantee** — once the WAL is flushed to disk, the transaction is safe. If the server crashes, RAM is lost, but on reboot Postgres replays the WAL back into the Heap and B-Tree files.
4. **The checkpoint** — periodically (e.g., every 5 minutes), a background **Checkpointer** process flushes all dirty pages from RAM to their permanent home in the Heap and B-Tree files.

---

## 4. Cassandra Bloom filters vs. Postgres mechanisms

Cassandra uses Bloom filters because a single partition's data can be fragmented across many SSTables. Postgres doesn't need them for core table lookups because a row lives in exactly one place inside the Heap file.

| Mechanism | Apache Cassandra | PostgreSQL |
|---|---|---|
| Data location | Fragmented across multiple chronological SSTables | Located in exactly one page inside the Heap |
| How it finds data | Checks Bloom filters across SSTables, then the partition index of matching files | Looks up the key in the B-Tree index to get the pointer `(Page, Row ID)`, then reads that Heap page directly |
| Memory map | Key/row cache maps partition keys to SSTable file locations | Buffer pool (`shared_buffers`) caches the exact 8KB blocks of Heap/Index files |

### Does Postgres ever use Bloom filters?

Yes, but only dynamically in memory during complex queries. For a large `JOIN`, Postgres may temporarily build a Bloom filter in RAM to discard non-matching rows before scanning the second table — it's not a permanent disk-routing structure like in Cassandra.

**Takeaway:** the split between the Heap (data rows) and the B-Tree (pointers to rows) is why Postgres updates carry more overhead than Cassandra's append-only model — every update touches both the Heap and every index. See [postgres-index-internal.md](postgres-index-internal.md) for how MVCC row versioning interacts with this.
