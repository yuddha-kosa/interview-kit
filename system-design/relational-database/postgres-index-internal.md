# Internal Mechanics of Postgres B-Tree Indexes & MVCC

---

## 1. The immutability and isolation problem (why we can't just "swap pointers")

When an `UPDATE` occurs in an MVCC architecture, the B-Tree index cannot simply overwrite its existing leaf pointer to redirect to the new heap tuple version.

- **The snapshot rule:** multiple transactions operate concurrently. A long-running read transaction that started before the update must still see the old tuple version, while a transaction starting after the update must see the new one.
- **Decoupled architecture:** the B-Tree index engine is blind to transaction states, snapshots, and row visibility — it acts as a strict physical mirror of whatever records exist in the Heap file. If two physical tuple versions live in the heap, two corresponding paths must exist in the index.

---

## 2. Storing duplicate keys in a standard B-Tree

In a textbook B-Tree, keys must be unique. PostgreSQL modifies this constraint to accommodate non-unique fields and historical MVCC duplicates through an internal composite key.

### The composite pair solution

The true key used by the internal sorting and traversal algorithms inside a Postgres B-Tree leaf node is a composite structure:

```text
Internal B-Tree Key = (Indexed Value, Tuple ID Pointer)
```

- **Tuple ID (TID):** every tuple in the Heap file has a unique physical disk address, written as `(Page Number, Offset Number)`.
- **Guaranteed uniqueness:** because every row version has a distinct physical location, appending the TID to the indexed value ensures no two keys in the B-Tree are ever truly identical.

### Visualizing the B-Tree leaf page

When you update a row, Postgres inserts a second entry into the B-Tree page, appending the TID to the sort key:

```text
8KB B-TREE LEAF PAGE
┌──────────────────────────────────────────────┐
│ Entry 1 → Key: "1" + TID: (Page 1, Offset 1)  │  <- old tuple
│ Entry 2 → Key: "1" + TID: (Page 1, Offset 2)  │  <- new tuple
└──────────────────────────────────────────────┘
```

### How Postgres searches this duplicate tree

When a query executes `WHERE user_id = 1`, the B-Tree engine navigates down to the first instance of `Key: "1"`. Because it knows duplicates can exist, it performs a linear scan across the leaf page, collecting every matching entry. It ships all matching TIDs to the Heap reader layer, which uses `xmin`/`xmax` snapshot filtering to pick the alive version.

---

## 3. The scope of standard index updates

Modifying a table record does not trigger a full, top-to-bottom rebalance or rewrite of the index structure.

- **Leaf localization:** for the vast majority of updates, Postgres routes directly to the 8KB leaf page containing that key range and appends the new entry `(Key, New TID)` into its unallocated buffer space (governed by the table's `fillfactor`).
- **Parent node isolation:** root and intermediate parent nodes are strict boundary markers used for navigation. They remain untouched by standard localized leaf modifications.

---

## 4. B-Tree page splits and duplicate key straddling

If a target 8KB leaf page has zero unallocated bytes left when a new duplicate key pointer arrives, Postgres performs a **page split**. This breaks the assumption that identical keys always sit on the same physical page.

```text
                 Parent Node Page
                (updated with new boundary range)
                         │
          ┌──────────────┴──────────────┐
          ▼                              ▼
   Leaf Page A                    Leaf Page B (new)
   Key: "1" (TID1)   right-link→  Key: "1" (TID51)
   Key: "1" (TID2)                Key: "1" (TID52)
```

### The allocation and rebalance mechanics

1. **New allocation:** Postgres allocates a brand-new, empty 8KB page at the end of the index file.
2. **The mid-key cut:** if the page is full of identical keys (e.g., a high-volume column value or heavy updates to a single row), Postgres splits the duplicate cluster down the middle, sorted by TID. 50% stay on the old page; 50% migrate to the new page.
3. **Upward propagation:** because a new page has been added, the change propagates to the parent node directly above. The parent updates its mapping to track the TID split threshold:
   - TIDs less than `(Page 5, Offset 51)` route to Leaf Page A
   - TIDs equal to or greater than `(Page 5, Offset 51)` route to Leaf Page B

---

## 5. Scanning across split pages: the right-link highway

When an index scan looks for a highly duplicated key that now straddles multiple physical blocks, it transitions horizontally using page metadata.

- **The right-link pointer:** every 8KB leaf page has a hidden header pointer called a **right-link**, giving the physical disk address of the next logical, sorted page to its right.
- **The traversal path:** Postgres navigates down the tree once to find the starting boundary on Leaf Page A, reads keys sequentially, hits the end of the block, and uses the right-link to jump straight to Leaf Page B horizontally — bypassing the need to traverse back up and down the parent nodes.
- **Scan termination:** the horizontal read continues until Postgres encounters a leaf cell where the indexed value changes to a new key. It halts the scan, aggregates all collected TIDs, and ships them to the Heap engine for MVCC snapshot visibility filtering.

---

## References

1. [Percona: PostgreSQL 14 B-Tree Index — Reduced Bloat with Bottom-Up Deletion](https://www.percona.com/blog/postgresql-14-b-tree-index-reduced-bloat-with-bottom-up-deletion/)
2. [Quest Blog: How Oracle B-Tree Indexes Work](https://blog.quest.com/product-post/how-oracle-b-tree-indexes-work/)
