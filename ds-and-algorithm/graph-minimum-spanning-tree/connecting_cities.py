import heapq

def minimum_cost(n, connections):

    graph = {}
    start = 0
    for src, dst, wt in connections:
        if src not in graph:
            graph[src] = []
        if dst not in graph:
            graph[dst] = []

        graph[src].append((dst, wt))
        graph[dst].append((src, wt))

        start = src
    
    heap = [(0, start)]
    visited = set()
    total_weight = 0

    while heap:
        weight, node = heapq.heappop(heap)

        if node in visited:
            continue
        
        total_weight += weight
        visited.add(node)

        for neigh, cost in graph[node]:
            if neigh not in visited:
                heapq.heappush(heap, (cost, neigh))
    
    if len(visited) != len(graph):
        return -1
    
    return total_weight




print(minimum_cost(3, [[1,2,5], [1,3,6], [2,3,1]]))
print(minimum_cost(4, [[1,2,3], [3,4,4]]))

'''
Time:  O(E log V)
Space: O(V + E)
'''