
import heapq

def  network_delay_time(times, n, k):
    graph = {}
    for i in range(len(times)):
        start_node = times[i][0]
        end_node = times[i][1]
        weight = times[i][2]
        val = (end_node, weight)
        if start_node in graph:
            graph[start_node].append(val)
        else:
           graph[start_node] = [val] 
    
    #print("graph: ", graph)

    dist = {}
    for i in range(n):
        dist[i+1] = float('inf')
    dist[k] = 0

    heap = []

    if k in graph:
        heapq.heappush(heap, (0, k))
    visited = set()
    max_time = 0

    while len(heap) > 0:

        dt, node = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        for neighbour, wt in graph[node]:
            if dist[neighbour] > dt + wt:
                dist[neighbour] = dt + wt
                if neighbour in graph:
                    heapq.heappush(heap, (dist[neighbour], neighbour))
                max_time = max(max_time, dist[neighbour])

    print(f"dist: {dist}")
    if max_time == 0 or len(dist) != n:
        return -1
    else:
        return max_time

n= 4
k= 2
print(network_delay_time([[2,1,1], [2,3,1], [3,4,1]], n, k))
print(network_delay_time([[1,2,1]], 2, 1))
print(network_delay_time([[1,2,1]], 2, 2))
'''
Time:
O(k log k) + O(n)

k log k = E log E = O(E log V)   [since log E and log V are
                                    the same Big-O class]
+ n = O(V)                        [dist initialization, no
                                    heap involved, no log factor]

Total: O(E log V + V) — this is actually a TIGHTER, more
precise version than the commonly-cited "O((V+E) log V)",
since the standard formula loosely multiplies BOTH terms by
log V for convenience, even though the V-only initialization
genuinely doesn't need a log factor.

Space:
graph:    O(k)   — one (end,weight) tuple per edge
dist:     O(n)   — one entry per vertex
visited:  O(n)   — one entry per vertex (missing from your total)
heap:     O(k)   — bounded by total pushes (≤ one per edge)

Total: O(k) + O(n) + O(n) + O(k) = O(k+n)
'''

def  network_delay_time_belman(times, n, k):
    graph = {}

    for vertex, neigh, weight in times:
        if vertex not in graph:
            graph[vertex] = []
        graph[vertex].append((weight, neigh))
    
    dist = {}
    for i in range(n):
        dist[i+1] = float('inf')
    dist[k] = 0

    if k in graph:
        for _ in range(n-1):
            for vertex in graph.keys():
                for weight, neighbour in graph[vertex]:
                    if dist[neighbour] > weight + dist[vertex]:
                        dist[neighbour] = weight + dist[vertex] 
    else:
        return -1    
    if float('inf') in dist.values():
        return -1
    else:
        return max(dist.values())


n= 4
k= 2
print(network_delay_time_belman([[2,1,1], [2,3,1], [3,4,1]], n, k))
print(network_delay_time_belman([[1,2,1]], 2, 1))
print(network_delay_time_belman([[1,2,1]], 2, 2))

'''
time: O(V*E)
Space: O(V)
'''