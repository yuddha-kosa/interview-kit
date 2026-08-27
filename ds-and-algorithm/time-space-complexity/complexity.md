O(1)       — constant    — doesn't matter how big input is, same work
O(log n)   — logarithmic — doubles input → one more step (binary search)
O(n)       — linear      — doubles input → doubles work
O(n log n) — linearithmic— sorting (merge sort, heap sort)
O(n²)      — quadratic   — doubles input → 4x work (nested loops)
O(2ⁿ)      — exponential — each element doubles work (brute force subsets)
O(n!)      — factorial   — all permutations



Interview Cheat Sheet:
Pattern you see in codeComplexity
Single loop O(n)
Two nested loops O(n²)
Loop that halves each iteration O(log n)
Loop + binary search inside O(n log n)
Recursive with 2 branches, no memo O(2ⁿ)
Recursive with memoUsually O(n)


log n: calculation
Start:        n elements
After step 1: n/2 elements
After step 2: n/4 elements
After step 3: n/8 elements
After step k: n/2ᵏ elements

n/2ᵏ = 1
n = 2ᵏ
k = log₂(n)     ← that's where log n comes from




One Sentence Rule to Remember:
Call stack space = how deep recursion goes (longest chain of pending calls)
Time = total number of calls × work per call

Algorithm          Time           Space (stack)   Space (extra)
─────────────────────────────────────────────────────────────
Factorial          O(n)           O(n)            O(1)
Fibonacci (naive)  O(2^n)         O(n)             O(1)
Binary search      O(log n)       O(log n)         O(1)
Merge sort (array) O(n log n)     O(log n)         O(n)
Quick sort         O(n log n) avg O(log n) avg      O(1)
Merge sort (list)  O(n log n)     O(log n)         O(1)



tree depth = log n

"at each level we are reading once" — exactly right, each
level of the B-tree = ONE disk page read (same idea as ONE
hop in union-find, or ONE comparison in BST search)

"total number of levels is log n" — exactly right in
PRINCIPLE, but the BASE of the logarithm matters, and it
depends on the BRANCHING FACTOR, not always base-2

Binary tree / union-find (branching factor = 2):
    levels = log₂(n)

B-tree with branching factor 100:
    levels = log₁₀₀(n)     <- MUCH SHALLOWER than log₂(n)
                              for the SAME n, since each level
                              "absorbs" 100x more entries,
                              not just 2x

For n=10,000, branching=100:
    100^1 = 100        (not enough to cover 10,000)
    100^2 = 10,000     (EXACTLY covers it) -> 2 levels needed

Why B-trees deliberately use a HIGH branching factor (not just 2, like a BST):
This connects directly to WHY database indexes use B-trees
specifically (not binary search trees): a HIGHER branching
factor means FEWER LEVELS needed for the SAME number of
entries — and since each LEVEL = one disk read (expensive,
compared to in-memory operations), MINIMIZING levels
minimizes expensive disk I/O.

log₁₀₀(n) grows MUCH slower than log₂(n) as n increases —
this is EXACTLY why real databases use branching factors in
the hundreds, not binary trees, for on-disk indexes.