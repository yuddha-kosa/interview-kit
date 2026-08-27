
def find(x, parent):
    if parent[x] == x:
        return x
    parent[x] = find(parent[x], parent)
    return parent[x]

def union(u, v, parent, rank):
    u_root = find(u, parent)
    v_root = find(v, parent)
    if u_root == v_root:
        return False
    if rank[u_root] > rank[v_root]:
        parent[v_root] = u_root
    else:
        parent[u_root] = v_root
        if rank[u_root] == rank[v_root]:
            rank[v_root] += 1
    return True

def min_cost_connect_pts(points):
    parent = list(range(len(points)))
    rank = [0]*(len(points))
    edges = []

    for i in range(len(points)-1):
        for j in range(i+1, len(points)):
            xi, yi = points[i]
            xj, yj = points[j]

            manh_dist = abs(xi-xj) + abs(yi-yj)
            edges.append((manh_dist, i, j))
    
    edges.sort()
    no_edges = 0
    total_wt = 0
    for wt, u, v in edges:
        if union(u, v, parent, rank):
            total_wt += wt
            no_edges += 1
        if no_edges == len(points)-1: # edges should be 1 less than the total number of vertex.
            break
    return total_wt


print(min_cost_connect_pts([[1,1], [3,3], [6,8], [4,2], [10,0]]))
print(min_cost_connect_pts([[5,5], [1,1], [2,2]]))

'''
Building the edges list:  O(n²)      -- nested loop over all pairs
Sorting the edges:        O(E log E) -- E = n²/2, so this is
                                        O(n² log(n²)) = O(n² log n)
                                        [since log(n²)=2log(n),
                                         and Big-O drops the
                                         constant factor 2]
Union-Find operations:    O(E α(n)) = O(n² α(n))
                                        -- smaller than the
                                           sorting term

Total = O(n²) + O(n² log n) + O(n² α(n))
      = O(n² log n)     [since log(n) grows faster than α(n),
                          and the O(n²) building cost is
                          dominated by the log(n) factor
                          multiplying it in the sorting step]

Total space = O(n) [parent] + O(n) [rank] + O(E) [edges list]
            = O(E)     [since E completely DOMINATES n here —
                         confirmed: 499,500 vs 1,000 for n=1000]

And since E = n²/2 for this COMPLETE graph specifically:
    O(E) = O(n²)
'''
# not correct
def min_cost_connect_pts1(points):
    total_wt = 0
    for i in range(len(points)-1):
        min_dist = float('inf')
        for j in range(i+1, len(points)):
            xi, yi = points[i]
            xj, yj = points[j]

            manh_dist = abs(xi-xj) + abs(yi-yj)
            min_dist = min(min_dist, manh_dist)
        total_wt += min_dist
    return total_wt

print(min_cost_connect_pts1([[1,1], [3,3], [6,8], [4,2], [10,0]]))
print(min_cost_connect_pts1([[5,5], [1,1], [2,2]]))