1. Define table[i] in WORDS first — a plain English sentence,
   BEFORE any math. If you can't say it in words, you're not
   ready to write the formula.

2. Find the base case(s) — the SMALLEST input where you know
   the answer without any calculation.

3. Ask: "if I'm AT position i, what could have happened
   JUST BEFORE this, that led me here?"
   — list out ALL the possible "last moves" or "last choices."

4. For EACH of those possible last moves, what SMALLER
   table value would I need to look up?

5. Combine those smaller values into a formula —
   usually a SUM (if movies are independent alternatives)
   or a MAX/MIN (if you're optimizing for best/worst).


The general signals that a problem is DP:

1. "Find the OPTIMAL (min/max/longest/shortest/count) ___"
   — optimization or counting language, not "find ALL ___"

2. The brute force involves checking many OVERLAPPING
   sub-cases repeatedly (same smaller question asked
   multiple times across different branches)

3. The answer to a BIGGER instance can be built from answers
   to SMALLER instances of the SAME problem


When you see a new problem, ask:

□ Am I looking for a BEST/OPTIMAL/COUNT answer (not "find all")?
□ If I tried brute force, would the SAME smaller sub-question
  get asked multiple times, in different branches?
□ Can I express "answer for size N" using "answer for size N-1
  (or smaller)" via a formula?

If YES to these — it's very likely DP, and your job becomes:
figure out WHAT table[?] represents, and what the RECURRENCE is.