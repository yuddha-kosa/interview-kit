import heapq
def max_probability(n, edges, succProb, start, end):

    graph = {}
    i = 0
    for src, dest in edges:
        if src not in graph:
            graph[src] = []
        graph[src].append((dest, succProb[i]))
        if dest not in graph:
            graph[dest] = []
        graph[dest].append((src, succProb[i]))
        i += 1
    
    dest = {}
    for i in range(n):
        dest[i] = 0
    dest[start] = -float('inf') 

    heap = [(-float('inf'), start)]
    visited = set() 
    while heap:
        prob, node = heapq.heappop(heap)
        #print(f"node: {node}, prob: {-prob}, dest: {dest}")
        if node == end:
            return -prob
        if node in visited or node not in graph:
            continue
        visited.add(node)
        for neig, p in graph[node]:
            if prob == -float('inf'):
                if dest[neig] < p:
                    dest[neig] = p
                    heapq.heappush(heap, (-dest[neig], neig))
            else:
                if dest[neig] < -(p*prob):
                    dest[neig] = -(p*prob)  
                    heapq.heappush(heap, (-dest[neig], neig))
    return 0

n = 3
edges = [[0, 1], [1, 2], [0, 2]]
successProb = [0.5, 0.5, 0.2]
start = 0
end = 2

print(max_probability(n, edges, successProb, start, end))
successProb = [0.5, 0.5, 0.3]
print(max_probability(n, edges, successProb, start, end))


print(max_probability(3, [[0,1]], [0.5], 0, 2))


'''
Time:  O((V+E) log V) — same shape as standard Dijkstra
Space: O(V+E)
'''