## 📑 Internal Mechanics of Postgres B-Tree Indexes & MVCC
------------------------------
## 1. The Immutability and Isolation Problem (Why We Can’t Just "Swap Pointers")
When an UPDATE occurs in an MVCC architecture, the B-Tree index cannot simply overwrite its existing leaf pointer to redirect to the new heap tuple version.

* 
* The Snapshot Rule: Multiple transactions operate concurrently. A long-running read transaction starting before the update must still see the old tuple version, while a transaction starting after the update must see the new one.
* Decoupled Architecture: The B-Tree index engine is completely blind to transaction states, snapshots, and row visibility. It acts as a strict physical mirror of whatever records exist inside the Heap file. If two physical tuple versions live in the heap, two corresponding paths must exist in the index.
* 

------------------------------
## 2. Storing Duplicate Keys in a Standard B-Tree
In a standard textbook B-Tree, keys must be unique. PostgreSQL modifies this constraint to naturally accommodate non-unique fields and historical MVCC duplicates through an internal composite structural design.
## The Composite Pair Solution
The true key used by the internal sorting and traversal algorithms inside a Postgres B-Tree leaf node is a composite structure:
Internal B-Tree Key = (Indexed Value, Tuple ID Pointer) 

* 
* Tuple ID (TID): Every tuple in the Heap file has a unique physical disk address, written as a pair representing its exact location: (Page Number, Offset Number).
* Guaranteed Uniqueness: Because every row version has a distinct physical location, appending the TID to the indexed value ensures that no two keys inside the B-Tree file are ever truly identical.

* Visualizing the B-Tree Leaf Page
When you update a row, Postgres inserts the second entry into the B-Tree page. Because it appends the TID to the sorting logic, it sorts them sequentially by their location. The leaf page physically looks like this:
💾 8KB B-TREE LEAF PAGE
┌────────────────────────────────────────────────────────┐
│ 🔑 Entry 1 ➔ Key: "1" + TID: (Page 1, Offset 1)        │  <-- Points to Old Tuple 1
├────────────────────────────────────────────────────────┤
│ 🔑 Entry 2 ➔ Key: "1" + TID: (Page 1, Offset 2)        │  <-- Points to New Tuple 2
└────────────────────────────────────────────────────────┘

* How Postgres Searches This Duplicate Tree
When a query executes WHERE user_id = 1, the B-Tree engine navigates down the nodes until it finds the first instance of Key: "1".Because it knows duplicates can exist, it doesn't stop. It performs a linear scan down the leaf page, collecting all entries that match Key: "1". It grabs both pointers and ships them to the Heap reader layer, which then uses the xmin/xmax snapshot filtering we discussed earlier to pick the alive one.
------------------------------
## 3. The Scope of standard Index Updates
Modifying a table record does not trigger a full, top-to-bottom rebalance or rewrite of the index file structure.

* 
* Leaf Localization: For the vast majority of updates, Postgres routes directly to the specific 8KB leaf page containing that key range and appends the new entry (Key, New TID) directly into its unallocated buffer space (governed by the table's fillfactor).
* Parent Node Isolation: Root and intermediate parent nodes are strictly boundary markers used for down-tree navigation. They remain completely untouched by standard localized leaf modifications.
* 

------------------------------
## 4. B-Tree Page Splits and Duplicate Key Straddling
If a target 8KB leaf page has absolutely zero unallocated bytes left when a new duplicate key pointer arrives, the database is forced to perform a Page Split. This event breaks the assumption that identical keys always sit on the same physical page.

               ┌────────────────────────┐
               │    Parent Node Page    │  <── (Updated with new boundary range)
               └───────────┬────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│  Leaf Page A    │                 │  Leaf Page B    │
│                 │                 │                 │
│ Key: "1" (TID1) │ ───Right-Link──►│ Key: "1" (TID51)│ <── (Brand New File Page)
│ Key: "1" (TID2) │                 │ Key: "1" (TID52)│
└─────────────────┘                 └─────────────────┘

## The Allocation and Rebalance Mechanics

   1. New Allocation: Postgres allocates a brand-new, empty 8KB page block at the end of the index file on disk.
   2. The Mid-Key Cut: If the page is full of identical keys (e.g., a high-volume column value or heavy updates to a single row), Postgres splits the duplicate cluster right down the middle, sorting them sequentially by their Tuple ID (TID). 50% stay on the old page; 50% migrate to the new page.
   3. Upward Propagation: Because a new boundary page has been added to disk, the change propagates up to the Parent Node directly above them. The parent node updates its mapping to track the TID split thresholds:
   * TIDs less than (Page 5, Offset 51) route to Leaf Page A
      * TIDs equal to or greater than (Page 5, Offset 51) route to Leaf Page B
   
------------------------------
## 5. Scanning Across Split Pages: The Right-Link Highway
When a query performs an index scan looking for a highly duplicated key that now straddles across multiple physical file blocks, it transitions horizontally using specialized page metadata. [1] 

* 
* The Right-Link Pointer: Every 8KB leaf page contains a hidden header metadata pointer called a Right-Link. This provides a direct physical disk address to the next logical, sorted page to its right.
* The Traversal Path: Postgres navigates down the tree once to find the starting boundary on Leaf Page A. It reads the keys sequentially, hits the end of the block, and uses the Right-Link to jump straight to Leaf Page B horizontally. It completely bypasses the need to traverse back up and down the parental nodes.
* The Scan Termination: The sequential horizontal read continues smoothly until Postgres encounters a leaf cell where the indexed value changes to a new key. The engine immediately halts the scan, aggregates all collected TIDs, and ships them to the Heap engine for MVCC snapshot visibility filtering. [2] 
* 

Would you like to combine these index mechanics notes with your previous notes on Cassandra's storage engine and the Postgres Heap layer to create one unified master database handbook?

[1] [https://www.percona.com](https://www.percona.com/blog/postgresql-14-b-tree-index-reduced-bloat-with-bottom-up-deletion/)
[2] [https://blog.quest.com](https://blog.quest.com/product-post/how-oracle-b-tree-indexes-work/)
