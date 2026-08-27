Imagine you need to connect N cities with electrical cable,
and each POSSIBLE cable route has a different COST. You want
EVERY city connected to the grid (directly or through other
cities), using the CHEAPEST possible total amount of cable —
with NO wasted/redundant connections (a cycle would mean
you're paying for cable you don't actually need).


A tree with V vertices ALWAYS has EXACTLY V-1 edges — no more,
no less (this is a property you've seen before: adding one
more edge to a tree ALWAYS creates a cycle, which is EXACTLY
what "Redundant Connection" was testing).

So: MST = pick exactly (V-1) edges, from all AVAILABLE edges,
such that everything stays connected, and the TOTAL weight
of those chosen edges is as SMALL as possible.


Kruskal's Algorithm:  sort ALL edges by weight, then GREEDILY
                      add the cheapest edge that DOESN'T create
                      a cycle — using UNION-FIND to check "would
                      this edge create a cycle?" (EXACTLY the
                      same check as Redundant Connection!)

Prim's Algorithm:     start from ANY vertex, and GREEDILY grow
                      the tree by always adding the CHEAPEST
                      edge that connects a NEW vertex to the
                      GROWING tree — using a MIN-HEAP (similar
                      structure to Dijkstra's approach)