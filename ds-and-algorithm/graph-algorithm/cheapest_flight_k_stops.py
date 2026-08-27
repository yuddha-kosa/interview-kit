import heapq

def find_cheapest_price(n, flights, src, dst, k):
    graph = {}
    for srcc, dest, cost in flights:
        if srcc not in graph:
            graph[srcc] = []
        graph[srcc].append((cost, dest))
    
    heap = [(0, 0, src)]

    '''
    * **No `visited`**: We keep all possible `(node, cost, hops)` states in the min-heap because the same node can be reached with different costs and different numbers of stops.
    * **`if hop > k: continue`**: The stop limit bounds how far we can explore, so cycles cannot continue indefinitely.

    '''
    while len(heap) > 0:
        cost, hop, node = heapq.heappop(heap)
        #print(f"node: {node}, cost: {cost}")
        if node == dst:
            return cost

        if hop > k:
            continue 

        for weight, neigh in graph[node]:
                heapq.heappush(heap, (cost+weight, hop+1, neigh))
    return -1




print(find_cheapest_price(4,[[0,1,100], [1,2,100], [2,0,100], [1,3,600], [2,3,200]], 0,3,1))
print(find_cheapest_price(3,[[0,1,100], [1,2,100], [0,2,500]], 0,2,1))
print(find_cheapest_price(3,[[0,1,100], [1,2,100], [0,2,500]], 0,2,0))

'''
time:
Number of heap operations ≈ K × E
Cost per heap operation ≈ log(K × E)
O(EK+EKlog(EK)) = O(EKlog(EK))

space: O(E+EK) = O(EK)
'''
print("************")

# this is wrong....
def find_cheapest_price_belman(n, flights, src, dst, k):
    graph = {}
    for srcc, dest, cost in flights:
        if srcc not in graph:
            graph[srcc] = []
        graph[srcc].append((cost, dest))
    
    dist = {}
    for i in range(n):
        dist[i] = (float('inf'),0)
    dist[src] = (0,0)

    for _ in range(k+1):
        for vertex in graph.keys():
            node_wt, hop = dist[vertex]
            if hop > k:
                continue
            for wt, neighbour in graph[vertex]:
                n_wt, _ = dist[neighbour] 
                if n_wt > wt+node_wt: 
                    dist[neighbour] = (wt+node_wt, hop+1)
    cost, hop = dist[dst]
    print(f"cost: {cost}, hop: {hop}")
    return cost


print(find_cheapest_price_belman(4,[[0,1,100], [1,2,100], [2,0,100], [1,3,600], [2,3,200]], 0,3,1))
print(find_cheapest_price_belman(3,[[0,1,100], [1,2,100], [0,2,500]], 0,2,1))
print(find_cheapest_price_belman(3,[[0,1,100], [1,2,100], [0,2,500]], 0,2,0))

'''
time: O(KE)
space: 0(E+V)
'''

'''
If you allow a JUST-UPDATED value to be used IMMEDIATELY
(in-place), a single round can let information "hop" through
MULTIPLE edges in one pass — like a chain reaction (A updates
B, B's fresh value IMMEDIATELY updates C, C's fresh value
IMMEDIATELY updates D — all within "round 0").

This breaks the ONE-TO-ONE correspondence between "round
number" and "hop count" that the whole algorithm depends on
to correctly enforce the k-stop budget.
'''

def find_cheapest_price_belman1(n, flights, src, dst, k):
    graph = {}
    for srcc, dest, cost in flights:
        graph.setdefault(srcc, []).append((cost, dest))
    
    dist = [float('inf')] * n
    dist[src] = 0
    
    for _ in range(k+1):
        new_dist = dist[:]              # snapshot — use OLD values
                                           # for THIS round's relaxation
        for vertex in graph:
            if dist[vertex] == float('inf'):
                continue
            for wt, neighbour in graph[vertex]:
                if new_dist[neighbour] > dist[vertex] + wt:
                    new_dist[neighbour] = dist[vertex] + wt
        dist = new_dist
    
    return dist[dst] if dist[dst] != float('inf') else -1
'''
"At most k STOPS" means "at most k INTERMEDIATE nodes," which
means "at most (k+1) EDGES" (k stops + 1 final edge to destination).

Since round index r covers paths of EXACTLY (r+1) edges, you
need round indices 0 through k (that's k+1 total rounds) to
cover ALL path lengths from 1 edge up to (k+1) edges — matching
EXACTLY "at most k stops."
'''