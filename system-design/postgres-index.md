Here’s a clean **structured summary of everything we covered about PostgreSQL internals**, organized so you can directly turn it into notes.

---

# 🧠 PostgreSQL Internals — Complete Summary (Heap + Index + B-tree)

---

# 1. 📦 Heap (Table Storage)

### What it is

* Heap = **actual table storage**
* NOT a tree
* Stored as **unordered pages**

### Structure

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

### Key properties

* Rows are **not sorted**
* Inserts go wherever space is available
* This is why full table scans are called **Seq Scan**

---

# 2. 🔍 Index (B-tree)

### What it is

* Separate structure from heap
* Used for fast lookup
* Typically implemented as **B-tree**

### One index = one B-tree

```text
Table
 ├── index on id   → B-tree #1
 ├── index on name → B-tree #2
 └── index on age  → B-tree #3
```

Each has:

* its own root
* internal pages
* leaf pages

---

# 3. 🌳 B-tree structure (Index)

### Not BST — multi-key node

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

### Why multiple children?

Because keys define ranges:

```text
<100 | 100–200 | 200–300 | >300
```

---

# 4. 📄 Pages = physical disk blocks

* Every node in B-tree = **one disk page**
* Page size ~8KB
* Root page is just one of these pages

---

# 5. 🧭 Root page

### Key facts

* There is **ONE root per index**
* Root is NOT named `idx_users_id`
* Name exists only in metadata

### How root is found

```text
Query → Planner → chooses index → uses OID → opens file → reads root page
```

### Root contains:

* separator keys
* pointers to child pages

NOT full tree

---

# 6. 🧾 Index name vs physical structure

### Index name (`idx_users_id`)

* stored in PostgreSQL catalog
* used by planner
* NOT used inside B-tree traversal

### Physical reality

```text
name → OID → index file → root page → traversal
```

---

# 7. 🔎 Query execution flow

Example:

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

---

# 8. 🧾 Leaf page (most important)

Leaf contains:

```text
key → TID (tuple id)
```

Example:

```text
345 → (heap_page 120, slot 7)
```

TID points to actual row in heap.

---

# 9. 🧱 Heap vs Index relationship

```text
Index (B-tree)
   ↓
points to
   ↓
Heap (actual row storage)
```

---

# 10. 🚀 Why B-tree is fast

### Binary tree

* height ≈ 20 for millions of rows

### B-tree

* fanout ~100–200
* height ≈ 3–5 even for billions of rows

Reason:

> each node reduces search space massively

---

# 11. 💾 CPU vs Disk cost

| Operation      | Cost               |
| -------------- | ------------------ |
| CPU comparison | nanoseconds        |
| Disk page read | micro/milliseconds |

👉 So reducing **disk reads is the main goal**

---

# 12. 🧠 Why B-tree beats BST

BST:

* 1 key per node
* tall tree
* many disk reads

B-tree:

* many keys per node
* wide tree
* very small height

---

# 13. 📌 Key clarifications you discovered

### ❌ Misconceptions corrected

* Heap is NOT a tree
* Root page is NOT named after index
* Full B-tree is NOT stored in one place
* Index name is NOT used during traversal
* Index and heap are separate structures

---

# 14. 🧠 Final mental model

Think of PostgreSQL like:

```text
Query
  ↓
Planner (chooses index)
  ↓
B-tree index (navigation system)
  ↓
Heap (actual data storage)
```

---

# ⭐ One-line summary

> PostgreSQL stores data in an unordered heap (table pages), and uses separate B-tree indexes (with root/internal/leaf pages stored as disk blocks) to efficiently locate rows via pointers (TIDs).

---

If you want next step, I can convert this into a **visual diagram cheat sheet (1-page interview revision sheet)** or explain **MVCC + dead tuples**, which completes the internal storage story.




# PostgreSQL B-Tree Index Notes

---

# 1. Heap vs Index

### Heap (Table Storage)

* Stores the **actual rows** of the table.
* Not sorted.
* Not a tree.
* Organized as 8 KB pages.

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

---

### Index (B-tree)

* Separate from the heap.
* Stores **keys** and pointers.
* Used to quickly locate rows.

Each index has its own B-tree.

```text
users table

├── Index(id)
├── Index(name)
└── Index(email)
```

Each index is an independent B-tree.

---

# 2. One B-tree = Many Pages

A B-tree is **not one object in memory**.

It is a collection of pages on disk.

```text
Root Page
      │
Internal Pages
      │
Leaf Pages
```

Every node of the B-tree is stored as **one 8 KB page**.

**Important**

```
Node = Page
```

---

# 3. What does logₘ(n) mean?

Suppose

* n = 10,000,000 keys
* m = 100 (fan-out)

Then

```
log₁₀₀(10,000,000) ≈ 4
```

This **does NOT mean the tree has only 4 pages.**

It means:

> From the root, PostgreSQL follows about **4 pages** (one page per level) to reach the correct leaf page.

The index may contain **hundreds of thousands of pages**, but a lookup only visits one page at each level.

---

# 4. B-tree Levels

Conceptually:

```text
Level 1
Root
1 page

↓

Level 2
100 pages

↓

Level 3
10,000 pages

↓

Level 4
Leaf pages
```

During a search:

* Read **one** page from Level 1.
* That page tells us **which one** page to read at Level 2.
* Repeat until reaching the leaf.

---

# 5. Structure of an Internal Page

An internal page contains:

* Separator keys
* Child pointers

Example:

```text
                Internal Page

        +-----------------------+
        |100|200|300|
        +-----------------------+
         |   |   |   |
         ▼   ▼   ▼   ▼
        P1  P2  P3  P4
```

---

# 6. Separator Keys

Separator keys divide the key space into regions.

Example:

```text
100
200
300
```

These are **separator keys**.

They separate all possible values into ranges.

---

# 7. Ranges

The ranges are **not stored**.

They are inferred from the separator keys.

Example:

```text
Separator Keys

100
200
300
```

Conceptually create:

```text
(-∞,100)

[100,200)

[200,300)

[300,+∞)
```

These ranges exist only conceptually while searching.

---

# 8. Child Pointers

Each range corresponds to one child page.

Conceptually:

```text
<100       → Page 8

100-200    → Page 28

200-300    → Page 34

>=300      → Page 44
```

The page actually stores the **child page numbers (block references)**, not the textual ranges.

---

# 9. Search Example

Search:

```text
id = 245
```

Root page:

```text
100
200
300
```

CPU compares:

```
245 > 200
245 < 300
```

Therefore:

```
Read Page 34
```

Page 34 contains another set of separator keys and child pointers.

Repeat until reaching a leaf page.

---

# 10. Leaf Pages

Leaf pages do **not** contain child pointers.

They contain:

```text
Key  → TID
```

Example:

```text
245 → (Heap Page 120, Slot 7)
```

The TID (Tuple ID) tells PostgreSQL exactly where the row is stored in the heap.

---

# 11. Fetching the Row

Lookup process:

```text
Query
    │
    ▼
Planner chooses index
    │
    ▼
Read Root Page
    │
    ▼
Read one Internal Page
    │
    ▼
Read one Leaf Page
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
*****
Planner
    │
    ▼
Choose idx_users_id
    │
    ▼
Read Root Page
    │
    ▼
Choose ONE child page
    │
    ▼
Read ONE internal page
    │
    ▼
Choose ONE child page
    │
    ▼
Read ONE leaf page
    │
    ▼
Get TID (Heap Page, Slot)
    │
    ▼
Read Heap Page
    │
    ▼
Return actual row
****
---

# 12. Important Distinction

### The page stores

* Separator keys
* Child pointers

### The page does NOT store

* Explicit ranges
* Actual table rows (except in some special index types, not standard B-tree indexes)

The CPU derives the ranges from the separator keys during traversal.

---

# 13. Mental Model

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

---

## Key Takeaways

* **Heap stores data; B-tree stores navigation information.**
* **One B-tree node = one disk page.**
* **`logₘ(n)` gives the number of pages read during a lookup (the tree height), not the total number of pages in the index.**
* **Internal pages contain separator keys and child pointers.**
* **Ranges are inferred from separator keys—they are not stored explicitly.**
* **Leaf pages store `key → TID`, and the TID points to the row in the heap.**



Here’s a clean **notes-ready summary** of what we clarified about B-tree levels, nodes, and “100 factor” confusion:

---

# 📘 PostgreSQL B-Tree Capacity & Level Growth (Notes)

## 1. Branching factor vs leaf capacity are different things

### Branching factor (≈100)

* Applies to **internal nodes only**
* Means:

  * Each internal page has up to **~100 child pointers**
  * Each node also has separator keys

👉 This determines:

> how many pages exist at each level of the tree

---

### Leaf page capacity (≈100 entries in our example)

* Applies only to **leaf pages**
* Each leaf page stores:

  * `(key → TID)` index entries
* Each entry points to heap row location

👉 This determines:

> how many rows a single leaf page can store

---

## 2. Key mistake to avoid (double counting)

❌ Wrong idea:

* “10,000 nodes × 100 keys per node × branching factor again”

This incorrectly multiplies the same factor twice.

---

## 3. Correct interpretation of levels

If branching factor = 100:

```text
Level 0:        1 page
Level 1:      100 pages
Level 2:   10,000 pages
Level 3: 1,000,000 pages (leaf level)
```

👉 This counts **pages (nodes), not rows**

---

## 4. Leaf pages store actual index entries

Each leaf page contains:

```text
(key → TID)
```

So if:

* 1 leaf page ≈ 100 entries
* 1,000,000 leaf pages exist

Then total indexed rows:

```text
1,000,000 × 100 = 100,000,000 rows
```

---

## 5. Correct mental model

### Two independent dimensions:

### (A) Tree structure growth

* Controlled by branching factor
* Determines number of pages per level

### (B) Data capacity per leaf

* Controlled by page size
* Determines rows per leaf page

---

## 6. Final intuition

> B-tree capacity is:

```
(# of leaf pages) × (entries per leaf page)
```

And:

```
# of leaf pages grows exponentially with height (fanout)
```

---

## 7. Key takeaway

* Branching factor builds the **shape of the tree**
* Leaf capacity stores the **actual data volume**
* You must NOT multiply branching factor twice at the same level

---

If you want next, I can give you a **1-page cheat sheet of B-tree operations (search, insert, split, root growth)** that ties everything together.


Good catch — **no, I did not include the “split” mechanics explicitly in that summary.** That summary was focused only on *capacity and level counting*, not structural changes.

Let me add the missing piece clearly and correctly.

---

# ➕ Add-on: What happens when a node becomes full (Split concept)

## 1. When does a split happen?

A **page (node)** splits when:

* It exceeds its capacity:

  * internal page → too many keys/pointers
  * leaf page → too many index entries

---

## 2. What happens in a leaf split?

Example (capacity = 4 for simplicity):

```text id="q9k3jd"
Leaf:
10 20 30 40 50   ❌ overflow
```

### Step 1: Split into two pages

```text id="k2n7qp"
Left Leaf        Right Leaf
10 20            30 40 50
```

---

### Step 2: Promote separator key

In B+ trees (PostgreSQL style):

* The **first key of right leaf** is copied upward

```text id="m8w2px"
Promoted key = 30
```

---

### Step 3: Parent update

Parent now gets:

```text id="t4zqv1"
30
```

and pointers:

```text id="f7p9la"
Left leaf   |   Right leaf
```

---

## 3. What happens if parent is full?

Then:

* Parent also splits
* A separator is pushed upward
* This may propagate up to the root

---

## 4. Root split (special case)

If root overflows:

```text id="r3x8cd"
New Root is created
Tree height increases by 1
```

---

## 5. Important invariant (VERY important)

> After every split, ALL leaves remain at the same depth.

Even though nodes are:

* split
* moved
* new root created

👉 The leaf level always stays uniform.

---

## 6. Updated mental model (complete)

Now combine everything:

### Capacity logic:

* branching factor → determines number of pages per level
* leaf capacity → determines rows per page

---

### Growth logic:

* insert fills leaf
* leaf splits → parent updated
* parent splits → may propagate upward
* root split → height increases

---

## 7. Final corrected note (one-liner)

> B-tree grows horizontally (more pages via splits) and occasionally vertically (root split increases height), while always keeping all leaves at the same level.

---

If you want next step, I can give you a **single unified diagram that connects: search + insert + split + logₘ(n) height** — that’s usually where everything finally clicks together.
