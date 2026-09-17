# PostgreSQL Storage & MVCC Architecture

This summary captures the mechanical behavior of how PostgreSQL manages, structures, and isolates data at the storage layer.

---

## 1. The core architecture: Heap vs. B-Tree

Unlike databases that bake data directly into index leaves, Postgres keeps data and indexes completely decoupled in separate physical files on disk.

- **The Heap file (the data):** the primary file storing raw table records (tuples). It's a collection of unstructured, fixed-size 8KB pages. Tuples are unsorted and dumped into whichever page has available space.
- **The B-Tree file (the index):** a separate file built for every index on a table. Leaves don't hold raw data — they store the indexed key and a Tuple ID (TID) pointer to a physical address `(Page Number, Offset Number)` inside the Heap.
- **The OID mapping (`pg_class`):** Postgres tracks the location of these trees and heaps using a system catalog table. Every table/index gets a unique Object Identifier (OID), and the physical disk file is literally named after it (e.g., `/base/13542/16384`).

---

## 2. The write path & WAL layer

To maximize performance, Postgres converts slow, random disk updates into fast, sequential memory writes using caching and a transaction log:

1. **Shared buffers (RAM):** incoming changes modify the Heap and B-Tree pages only in memory first. These are "dirty pages."
2. **Write-Ahead Log / WAL (disk append):** before acknowledging success, Postgres appends a brief log of the transaction to the sequential WAL file on disk. This guarantees durability if the server crashes before RAM is flushed.
3. **The checkpoint:** a background process periodically flushes all dirty pages from `shared_buffers` out to their permanent homes in the Heap and B-Tree files.

---

## 3. MVCC & row versioning in the Heap

Postgres enforces Multi-Version Concurrency Control (MVCC) to let transactions read and write simultaneously without locking tables.

- **Metadata flags:** every tuple in an 8KB heap page has internal tracking headers:
  - `xmin`: the transaction ID that inserted this version.
  - `xmax`: the transaction ID that updated or deleted this version (0 if still active).
- **The anatomy of an `UPDATE`:**
  - The old tuple is left completely intact on disk. Its `xmax` is set to the current transaction ID to mark it dead to future transactions.
  - A brand-new version of the tuple is appended to open space in an 8KB page, with `xmin` set to the current transaction ID.

---

## 4. The impact on B-Tree indexes

Because updates duplicate and move rows within the Heap file, the index architecture suffers write-side effects:

- **Index multiplication:** every time a row gets a new version in the heap, all indexes on that table must insert a new pointer to the new location — even if the indexed column didn't change.
- **Dead pointers in the B-Tree:** old index keys (e.g., `Key: "Old Phone" -> Old Tuple`) remain in the B-Tree file. They can't be instantly deleted because ongoing, older transactions might still need them for a historically accurate view of the data.

---

## 5. How queries pick the right version

If an index search returns multiple pointers for the same logical record, Postgres resolves it via metadata filtering:

1. The query executor follows the B-Tree pointers and pulls all matching tuples from the Heap pages into RAM.
2. It evaluates each tuple's `xmin`/`xmax` metadata against the query's own snapshot (the list of active transaction IDs when the query started).
3. **Filtration:** it discards any tuple marked dead (`xmax`) or uncommitted to its specific snapshot, returning exactly one valid version to the application.

---

## 6. Table bloat & the remediation layer

Accumulating dead tuples in the Heap and dead pointers in the B-Tree causes **bloat**, wasting disk space and slowing page scans. Postgres resolves this via two mechanisms:

- **`LP_DEAD` flagging (micro-cleanup):** regular index reads that discover dead tuples flag the corresponding B-Tree leaf as `LP_DEAD`. Future write operations on that index page proactively overwrite those slots.
- **The `VACUUM` process (macro-cleanup):** a background worker that runs a two-pass routine:
  1. Scans the Heap file to assemble a list of all dead tuple addresses.
  2. Scans the B-Tree index files to permanently purge and unlink keys pointing to those dead addresses, reclaiming the space for future inserts.

See [postgres-deletion-vaccum.md](postgres-deletion-vaccum.md) for more detail on `VACUUM` vs `VACUUM FULL`, and [postgres-index-internal.md](postgres-index-internal.md) for B-Tree internals.
