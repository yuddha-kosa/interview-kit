# PostgreSQL B-Tree Index — Study Notes

Structured notes on PostgreSQL internals: Heap storage, B-tree indexes, and how a lookup traverses from query to row.

---

## Part 1: Heap + Index + B-tree Fundamentals

### 1. 📦 Heap (table storage)

**What it is**

- Heap = **actual table storage**
- Not a tree
- Stored as **unordered pages**

**Structure**

```text
Heap (table)
│
├── Page 1 (8 KB)
├── Page 2
├── Page 3
└── ...
```

Each page contains:

```text
Page
------------------
| Row | Row | Row |
------------------
```

**Key properties**

- Rows are **not sorted**
- Inserts go wherever space is available
- This is why full table scans are called **Seq Scan**

### 2. 🔍 Index (B-tree)

**What it is**

- Separate structure from the heap
- Used for fast lookup
- Typically implemented as a **B-tree**

**One index = one B-tree**

```text
Table
 ├── index on id   → B-tree #1
 ├── index on name → B-tree #2
 └── index on age  → B-tree #3
```

Each has its own root, internal pages, and leaf pages.

### 3. 🌳 B-tree structure (index)

**Not a BST — multi-key node**

Each node stores:

```text
[k keys] → [k+1 pointers]
```

Example:

```text
|100|200|300|
 ↓   ↓   ↓   ↓
P1  P2  P3  P4
```

**Why multiple children?**

Because keys define ranges:

```text
<100 | 100–200 | 200–300 | >300
```

### 4. 📄 Pages = physical disk blocks

- Every node in a B-tree = **one disk page**
- Page size ~8KB
- The root page is just one of these pages

### 5. 🧭 Root page

**Key facts**

- There is **one root per index**
- The root is not named `idx_users_id`
- The index name exists only in metadata

**How the root is found**

```text
Query → Planner → chooses index → uses OID → opens file → reads root page
```

**Root contains:**

- Separator keys
- Pointers to child pages

Not the full tree.

### 6. 🧾 Index name vs. physical structure

**Index name (`idx_users_id`)**

- Stored in the PostgreSQL catalog
- Used by the planner
- Not used inside B-tree traversal

**Physical reality**

```text
name → OID → index file → root page → traversal
```

### 7. 🔎 Query execution flow

```sql
SELECT * FROM users WHERE id = 345;
```

Steps:

```text
1. Planner sees WHERE id
2. Picks idx_users_id
3. Opens index file
4. Reads root page
5. Traverses internal pages
6. Reaches leaf page
7. Gets (key → TID)
8. Uses TID to fetch heap row
```

### 8. 🧾 Leaf page (most important)

Leaf contains:

```text
key → TID (tuple id)
```

Example:

```text
345 → (heap_page 120, slot 7)
```

The TID points to the actual row in the heap.

### 9. 🧱 Heap vs. index relationship

```text
Index (B-tree)
   ↓
points to
   ↓
Heap (actual row storage)
```

### 10. 🚀 Why a B-tree is fast

**Binary tree:** height ≈ 20 for millions of rows.

**B-tree:** fanout ~100–200, height ≈ 3–5 even for billions of rows.

Reason: each node reduces the search space massively.

### 11. 💾 CPU vs. disk cost

| Operation | Cost |
|---|---|
| CPU comparison | nanoseconds |
| Disk page read | micro/milliseconds |

So reducing **disk reads is the main goal**.

### 12. 🧠 Why a B-tree beats a BST

**BST:** one key per node, tall tree, many disk reads.

**B-tree:** many keys per node, wide tree, very small height.

### 13. 📌 Key clarifications

**Misconceptions corrected:**

- The heap is not a tree
- The root page is not named after the index
- The full B-tree is not stored in one place
- The index name is not used during traversal
- The index and heap are separate structures

### 14. 🧠 Final mental model

```text
Query
  ↓
Planner (chooses index)
  ↓
B-tree index (navigation system)
  ↓
Heap (actual data storage)
```

> **One-line summary:** PostgreSQL stores data in an unordered heap (table pages), and uses separate B-tree indexes (with root/internal/leaf pages stored as disk blocks) to efficiently locate rows via pointers (TIDs).

---

## Part 2: B-Tree Index Notes

### 1. Heap vs. index

**Heap (table storage)**

- Stores the **actual rows** of the table
- Not sorted
- Not a tree
- Organized as 8 KB pages

```text
Heap
│
├── Page 1
├── Page 2
├── Page 3
└── ...
```

Each page contains actual rows:

```text
Page 10

Row 1
Row 2
Row 3
...
```

**Index (B-tree)**

- Separate from the heap
- Stores **keys** and pointers
- Used to quickly locate rows

Each index has its own B-tree:

```text
users table

├── Index(id)
├── Index(name)
└── Index(email)
```

### 2. One B-tree = many pages

A B-tree is **not one object in memory** — it is a collection of pages on disk.

```text
Root Page
      │
Internal Pages
      │
Leaf Pages
```

Every node of the B-tree is stored as **one 8 KB page**.

> `Node = Page`

### 3. What does logₘ(n) mean?

Suppose `n = 10,000,000` keys and `m = 100` (fan-out). Then:

```text
log₁₀₀(10,000,000) ≈ 4
```

This **does not** mean the tree has only 4 pages. It means: from the root, PostgreSQL follows about **4 pages** (one page per level) to reach the correct leaf page.

The index may contain **hundreds of thousands of pages**, but a lookup only visits one page at each level.

### 4. B-tree levels

Conceptually:

```text
Level 1: Root          1 page
Level 2:              100 pages
Level 3:           10,000 pages
Level 4 (leaf):  1,000,000 pages
```

During a search: read **one** page from Level 1. That page tells you **which one** page to read at Level 2. Repeat until reaching the leaf.

### 5. Structure of an internal page

An internal page contains separator keys and child pointers:

```text
                Internal Page

        +-----------------------+
        |100|200|300|
        +-----------------------+
         |   |   |   |
         ▼   ▼   ▼   ▼
        P1  P2  P3  P4
```

### 6. Separator keys

Separator keys divide the key space into regions, e.g. `100`, `200`, `300`. They separate all possible values into ranges.

### 7. Ranges

The ranges themselves are **not stored** — they are inferred from the separator keys.

```text
Separator Keys: 100, 200, 300

Conceptually create:
(-∞,100)
[100,200)
[200,300)
[300,+∞)
```

These ranges exist only conceptually, during the search.

### 8. Child pointers

Each range corresponds to one child page:

```text
<100       → Page 8
100-200    → Page 28
200-300    → Page 34
>=300      → Page 44
```

The page actually stores the **child page numbers (block references)**, not the textual ranges.

### 9. Search example

Search for `id = 245`. Root page: `100 | 200 | 300`.

The CPU compares `245 > 200` and `245 < 300`, so it reads Page 34. Page 34 contains another set of separator keys and child pointers — repeat until reaching a leaf page.

### 10. Leaf pages

Leaf pages do **not** contain child pointers. They contain `Key → TID`, e.g.:

```text
245 → (Heap Page 120, Slot 7)
```

The TID (Tuple ID) tells PostgreSQL exactly where the row is stored in the heap.

### 11. Fetching the row

```text
Query
  │
  ▼
Planner chooses idx_users_id
  │
  ▼
Read Root Page
  │
  ▼
Read Internal Page(s)
  │
  ▼
Read Leaf Page
  │
  ▼
Get TID (Heap Page, Slot)
  │
  ▼
Read Heap Page
  │
  ▼
Return actual row
```

### 12. Important distinction

**The page stores:** separator keys, child pointers.

**The page does not store:** explicit ranges, actual table rows (except in some special index types, not standard B-tree indexes).

The CPU derives the ranges from the separator keys during traversal.

### 13. Mental model

Think of each internal page as a decision point:

```text
                 PAGE

            100   200   300
             │     │     │
             ▼     ▼     ▼

        Which range contains my key?

             │
             ▼

      Follow exactly ONE child page
```

Each page narrows the search space until a leaf page provides the pointer (TID) to the actual row in the heap.

### Key takeaways

- Heap stores data; B-tree stores navigation information.
- One B-tree node = one disk page.
- `logₘ(n)` gives the number of pages read during a lookup (the tree height), not the total number of pages in the index.
- Internal pages contain separator keys and child pointers.
- Ranges are inferred from separator keys — they are not stored explicitly.
- Leaf pages store `key → TID`, and the TID points to the row in the heap.

---

## Part 3: B-Tree Capacity & Level Growth

Notes on B-tree levels, nodes, and the "branching factor of 100" mental model.

### 1. Branching factor vs. leaf capacity are different things

**Branching factor (≈100)**

- Applies to **internal nodes only**
- Each internal page has up to **~100 child pointers**, plus separator keys
- Determines how many pages exist at each level of the tree

**Leaf page capacity (≈100 entries in this example)**

- Applies only to **leaf pages**
- Each leaf page stores `(key → TID)` index entries, one per heap row
- Determines how many rows a single leaf page can store

### 2. Key mistake to avoid (double counting)

Wrong idea: "10,000 nodes × 100 keys per node × branching factor again." This incorrectly multiplies the same factor twice.

### 3. Correct interpretation of levels

If branching factor = 100:

```text
Level 0:        1 page
Level 1:      100 pages
Level 2:   10,000 pages
Level 3: 1,000,000 pages (leaf level)
```

This counts **pages (nodes), not rows**.

### 4. Leaf pages store actual index entries

If 1 leaf page ≈ 100 entries and 1,000,000 leaf pages exist, then total indexed rows:

```text
1,000,000 × 100 = 100,000,000 rows
```

### 5. Correct mental model

Two independent dimensions:

- **(A) Tree structure growth** — controlled by branching factor, determines pages per level.
- **(B) Data capacity per leaf** — controlled by page size, determines rows per leaf page.

### 6. Final intuition

```text
B-tree capacity = (# of leaf pages) × (entries per leaf page)
# of leaf pages grows exponentially with height (fanout)
```

### 7. Key takeaway

- Branching factor builds the **shape of the tree**.
- Leaf capacity stores the **actual data volume**.
- You must not multiply branching factor twice at the same level.

---

## Part 4: Node Splits

What happens when a page (node) fills up — the mechanics of a B-tree split.

### 1. When does a split happen?

A page (node) splits when it exceeds its capacity — an internal page has too many keys/pointers, or a leaf page has too many index entries.

### 2. What happens in a leaf split?

Example (capacity = 4 for simplicity):

```text
Leaf:
10 20 30 40 50   ❌ overflow
```

**Step 1: split into two pages**

```text
Left Leaf        Right Leaf
10 20            30 40 50
```

**Step 2: promote the separator key**

In B+ trees (PostgreSQL style), the **first key of the right leaf** is copied upward:

```text
Promoted key = 30
```

**Step 3: parent update**

The parent now gets key `30` and pointers to `Left leaf | Right leaf`.

### 3. What happens if the parent is full?

Then the parent also splits, a separator is pushed upward, and this may propagate up to the root.

### 4. Root split (special case)

If the root overflows, a new root is created and the tree height increases by 1.

### 5. Important invariant

> After every split, **all leaves remain at the same depth.**

Even though nodes are split, moved, or a new root is created, the leaf level always stays uniform.

### 6. Updated mental model (complete)

**Capacity logic:**

- Branching factor → determines the number of pages per level.
- Leaf capacity → determines rows per page.

**Growth logic:**

- Insert fills leaf → leaf splits → parent updated.
- Parent splits → may propagate upward.
- Root splits → height increases.

### 7. Final corrected note

> A B-tree grows horizontally (more pages via splits) and occasionally vertically (a root split increases height), while always keeping all leaves at the same level.
