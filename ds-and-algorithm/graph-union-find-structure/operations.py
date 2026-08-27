class UnionFind:
    def __init__(self, n):
        # this is like a pointer, the index contains the node and the value contains the parent.
        # when index and value are same that means the node is pointing to itself and that means
        # the node itself is the root/representative of the union structure (disjoint set).
        self.parent = list(range(n))
    
    def find(self, x):
        if self.parent[x] == x:  
            return self.parent[x]
        return self.find(self.parent[x])

    def union(self, x, y):
        rep_x = self.find(x)
        rep_y = self.find(y)

        if rep_x != rep_y:
            self.parent[rep_x] = rep_y
            return True
        
        return False

'''
Time:  O(depth) — dominated by the two find() calls
Space: O(1) extra (beyond find's recursion stack)
'''

uf = UnionFind(10)

# Test 1: initially, everyone is their own group
print(uf.find(5))              # expect 5
print(uf.find(0) == uf.find(1))  # expect False

# Test 2: merge some groups
uf.union(1, 2)
uf.union(2, 3)
uf.union(4, 5)

# Test 3: check groups formed correctly
print(uf.find(1) == uf.find(3))  # expect True (1-2-3 merged)
print(uf.find(1) == uf.find(4))  # expect False (still separate)
print(uf.find(4) == uf.find(5))  # expect True

# Test 4: merging groups that share a common member
uf.union(3, 4)
print(uf.find(1) == uf.find(5))  # expect True NOW (all merged: 1-2-3-4-5)

# Test 5: union returns False for already-connected nodes
print(uf.union(1, 5))            # expect False (already same group)

# Test 6: untouched nodes remain separate
print(uf.find(7))                # expect 7
print(uf.find(1) == uf.find(7))  # expect False

# Test 7: chain-like merging (tests deeper find() chains)
uf.union(6, 7)
uf.union(7, 8)
uf.union(8, 9)
print(uf.find(6) == uf.find(9))  # expect True (6-7-8-9 all merged)

class UnionFindOpt:
    def __init__(self, n):
        # this is like a pointer, the index contains the node and the value contains the parent.
        # when index and value are same that means the node is pointing to itself and that means
        # the node itself is the root/representative of the union structure (disjoint set).
        self.parent = list(range(n))
        self.rank = [0]*n
    
    def find(self, x):
        if self.parent[x] == x:  
            return self.parent[x]
        self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rep_x = self.find(x)
        rep_y = self.find(y)

        if rep_x == rep_y:
            return
        '''
        If rep_x's rank is STRICTLY GREATER than rep_y's, attaching
        rep_y underneath rep_x does NOT increase the OVERALL tree's
        height — rep_x's subtree was ALREADY deeper, so absorbing a
        SHORTER tree underneath doesn't change the max depth.

        Only when BOTH trees were EQUALLY tall does merging them
        create a tree that's ONE level taller than either original —
        hence rank increases ONLY in that specific case.
        '''
        if self.rank[rep_x] > self.rank[rep_y]:
            self.parent[rep_y] = rep_x
        else:
            self.parent[rep_x] = rep_y
            if self.rank[rep_x] == self.rank[rep_y]: 
                self.rank[rep_y] += 1


'''
The key fact: a tree with RANK r must contain AT LEAST 2^r
nodes.

Proof sketch (by induction): a rank-0 tree has ≥1 node
(trivially). A rank-(r+1) tree is ONLY created by merging
TWO EQUAL-rank-r trees — each ALREADY guaranteed to have ≥2^r
nodes (by induction) — so the merged tree has ≥2×2^r = 2^(r+1)
nodes.

Time:  O(log n) per find/union — rank guarantees tree depth
       stays logarithmic
Space: O(n) for parent + rank arrays
'''


'''
This is NOT a sum of decreasing work. It's simply:

    "How many PARENT-POINTERS do I follow to reach the root?"

If the tree has DEPTH d, then find() does EXACTLY d steps
(hops), each step being O(1) work (just checking one array
value: parent[x]).

Time = (number of hops) × (work per hop)
     = d × O(1)
     = O(d)

Since rank guarantees d ≤ log(n), this gives:
     Time = O(log n)
'''