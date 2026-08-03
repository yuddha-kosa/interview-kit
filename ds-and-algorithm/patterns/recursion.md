Before writing any recursive function, answer:

1. Base case — when does recursion stop?
2. One step — what does THIS call do (the "smaller piece" of work)?
3. Smaller problem — what smaller version do you recurse on?



Backtracking — One Sentence
Try a choice → recurse → if it doesn't lead to a solution,
UNDO the choice (backtrack) → try the next choice.

The Template:
Template A — explicit binary choice (what you just wrote, for subsets):
def backtrack(index):
    if base_case:
        save and return
    # choice 1
    make(choice_1)
    backtrack(...)
    undo(choice_1)
    # choice 2
    backtrack(...)   # "skip" has nothing to undo

Template B — loop over many choices (for permutations, combination sum):
def backtrack(path, choices):
    if is_solution(path):
        result.append(path[:])    # save a COPY
        return                     # or continue, depending on problem

    for choice in choices:
        if is_valid(choice, path):
            path.append(choice)        # make choice
            backtrack(path, choices)   # explore
            path.pop()                 # undo choice (backtrack)

The Three Questions, Backtracking Version
1. Base case — when is path a complete/valid solution?
2. Choices — what are the options at this step?
3. Undo — how do you remove a choice before trying the next?

1. Base case?
   sum(current) == target → save and return
   sum(current) > target  → return

2. One call does?
   make: current.append(nums[index])
   explore: backtrack(same index)   ← reuse allowed
   undo: current.pop()

3. Smaller problem?
   loop from current index forward — never backwards
   this prevents duplicate combinations



Time complexity: The general procedure — works for ANY recursive algorithm:
Step 1: Identify what the recursion tree looks like
        (how many children does each node have?)

Step 2: Count how many nodes exist at EACH level

Step 3: Sum nodes across ALL levels = total recursive calls

Step 4: Multiply by work done PER node (not counting recursive calls)
        = total time complexity



Intuition:
You asked: "isn't level like a loop, where work-per-iteration
            can differ?"

YES — exactly. The general formula for ANY recursive algorithm is:

  Total time = Σ (over all depths d) [ nodes_at_depth(d) × work_per_node_at_depth(d) ]

Merge sort:  nodes_at_depth(d) = 2^d,  work_per_node(d) = n/2^d
             product at every d = n  (constant!)
             sum over log(n) levels = n × log(n)

Subsets:     nodes_at_depth(d) = 2^d,  work_per_node(d) = O(1) for d<n,
                                                            O(n) for d=n (leaf)
             product at depth d<n = 2^d  (GROWING with d)
             product at depth d=n = 2^n × n
             sum ≈ dominated by the LAST term = O(2^n × n)


Geometric series formula:
2^0 + 2^1 + 2^2 + ... + 2^n = 2^(n+1) − 1


General geometric series (any ratio r, not just 2):
a + ar + ar² + ... + ar^n = a × (r^(n+1) − 1) / (r − 1)

For a=1, r=2:
= (2^(n+1) − 1) / (2 − 1)
= 2^(n+1) − 1

n=0: 2^0 = 1           → 2^1 − 1 = 1  ✓
n=1: 2^0+2^1 = 1+2 = 3 → 2^2 − 1 = 3  ✓
n=2: 1+2+4 = 7         → 2^3 − 1 = 7  ✓
n=3: 1+2+4+8 = 15      → 2^4 − 1 = 15 ✓



Time  = Σ over ALL levels [ nodes_at_level × work_per_node ]
        (cumulative — everything that EVER executed counts)

Space = max recursion depth (frame count)
        + Σ over all frames ALIVE at the deepest moment
          [ data held by that frame ]
        (snapshot — only what's simultaneously alive counts)

Space = how many frames are stacked (depth)
        + how much data is alive across ALL those stacked
          frames at the single worst moment
        (NOT just one level's data — but in these 3 examples,
         either the data is O(1) per frame or sums to O(n)
         across frames, so your "depth + data" gives the
         right answer every time)

Exact total for subsets:
Total = (internal node work) + (leaf node work)
      = (2^(n+1) - 1 - 2^n) + (2^n × n)        [internal = all nodes except leaves]
      = (2^n - 1) + (2^n × n)                   [since 2^(n+1)-2^n = 2^n]
      ≈ O(2^n) + O(2^n × n)
      = O(2^n × n)    [second term dominates the first]

✓ Time: SUM work across ALL levels (everything that ever ran)
✓ Space: depth + data alive at the worst single moment
✓ Merge sort: log n (depth) + n (arrays summed) = O(n)
✓ Permutation: n (depth) + n (path) = O(n)
✓ Subset: n (depth) + n (path) = O(n)


Backtracking Complexity Cheat Sheet:
| Problem             | What we are generating       | Time Complexity           | Space (Auxiliary) | Key intuition                                       |
| ------------------- | ---------------------------- | ------------------------- | ----------------- | --------------------------------------------------- |
| **Combination Sum** | Combinations with repetition | (O(n^{T/M})) (worst case) | (O(T/M))          | depth = how many times you can pick smallest number |
| **Subsets**         | All subsets                  | (O(2^n \cdot n))          | (O(n))            | each element is either taken or not                 |
| **Permutations**    | All orderings                | (O(n \cdot n!))           | (O(n))            | each level fixes one position                       |
