def kruskal(edges, n):
    parent = list(range(n))
    rank = [0]*n

    tree = {}

    def find(x):
        if parent[x] == x:
            return x
        parent[x] = find(parent[x])
        return parent[x]
    
    def union(u, v, wt):
        u_r = find(u)
        v_r = find(v)

        if u_r == v_r:
            return False

        if rank[u_r] > rank[v_r]:
            parent[v_r] = u_r
            if u not in tree:
                tree[u] = []
            tree[u].append((v, wt))
        else:
            parent[u_r] = v_r
            if v not in tree:
                tree[v] = []
            tree[v].append((u, wt))
            if rank[u_r] == rank[v_r]:
                rank[v_r] += 1
        return True

    totalWeight = 0
    edges.sort(key=lambda x: x[2])
    for src, dst, wt in edges:
        if union(src, dst, wt):
           totalWeight += wt
    print("Tree: ", tree)
    return totalWeight 

'''
Time:  O(E log E) for sorting + O(E α(V)) for union-find ops
       = O(E log E) overall (sorting dominates)
Space: O(V + E)
'''

vertices1 = 3
edges1 = [(0,1,1), (1,2,1), (0,2,10)]
# Expected MST weight = 2
print(kruskal(edges1, vertices1))

vertices2 = 4  # A=0, B=1, C=2, D=3
edges2 = [(0,1,4), (0,2,1), (1,2,2), (1,3,5), (2,3,8)]
# Expected MST weight = 8 (same graph, same answer as Prim's gave)
print(kruskal(edges2, vertices2))