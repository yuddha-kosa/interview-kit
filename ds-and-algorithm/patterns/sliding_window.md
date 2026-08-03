Pattern 1 — Fixed Window
Window size is given (k or len(txt1))
Size never changes — just slides

1. Build initial window of size k
2. Check initial window
3. Loop from k to end:
   - add right element
   - remove left element (index i-k)
   - check window

Problems:
→ Permutation in string
→ Max sum of k consecutive elements
→ Find all anagrams in string

Pattern 2 — Variable Window (expand/shrink)
Window size changes based on constraint
Expand right freely, shrink left when violated

1. left = 0
2. Loop right from 0 to end:
   - add right element to window
   - while constraint violated:
       remove left element
       left += 1
   - update answer (window is now valid)

Problems:
→ Longest substring without repeating chars
→ Longest repeating char replacement
→ Minimum window substring

Pattern 3 — Variable Window (find shortest)
Same as pattern 2 but looking for minimum
Shrink as much as possible while still valid

1. left = 0
2. Loop right from 0 to end:
   - add right element
   - while constraint STILL SATISFIED:
       update answer
       remove left element
       left += 1

Problems:
→ Minimum window substring
→ Shortest subarray with sum >= k

How to identify which pattern:
Fixed size given (k)?
    → Pattern 1

Looking for longest/maximum?
    → Pattern 2

Looking for shortest/minimum?
    → Pattern 3

All three patterns share one idea:
"Maintain a window that satisfies a constraint
 by expanding right and shrinking left"

The difference is only:
Pattern 1: shrink by exactly 1 (fixed size)
Pattern 2: shrink until valid (variable, maximize)
Pattern 3: shrink while valid (variable, minimize)