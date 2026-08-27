import heapq

def dijkstra(graph, source):
    current_dist = {}
    for node in graph:
        if node == source:
            current_dist[node] = 0
        else:
            current_dist[node] = float('inf')

    path = [source]
    min_heap = []
    heapq.heappush(min_heap, (0, source, path))

    final_path = {}
    while len(min_heap) > 0:
        dist, node, path = heapq.heappop(min_heap)
        #print(f"dist: {dist}, node: {node}")

        '''
        Once a node's TRUE shortest distance is found and processed
        (the FIRST, SMALLEST pop of that node), any LATER pop of the
        SAME node (with a LARGER, stale distance) can NEVER discover
        anything better for its neighbors — because relaxing with a
        BIGGER starting distance can only produce EQUAL OR WORSE
        results, never better.
        '''
        if dist > current_dist[node]:
            continue

        neighbours = graph[node]
        for neighbour, weight in neighbours.items():
            if current_dist[neighbour] > dist + weight:
                current_dist[neighbour] = dist + weight
                heapq.heappush(min_heap, (current_dist[neighbour], neighbour, path+[neighbour]))
                final_path[neighbour] = path+[neighbour] # just to visualize the path 
    
    print(final_path)
    return current_dist

graph = {
    'A': {'B': 4, 'C': 1},
    'B': {'D': 1},
    'C': {'B': 2, 'D': 5},
    'D': {}
}

graph2 = {
    'A': {'B': 2, 'C': 5},
    'B': {'C': 1, 'D': 4},
    'C': {'D': 1},
    'D': {'E': 3},
    'E': {}
}

print(dijkstra(graph, "A"))
print(dijkstra(graph2, "A"))


'''
current_dist:  O(V)
min_heap:      O(E)

Total Space = O(V) + O(E) = O(V + E)

Time:

Total pushes ≤ E → each push costs O(log(heap size)) = O(log E)
Total pops   ≤ E (since every push eventually gets popped) →
              each pop ALSO costs O(log E)

Total heap operation cost = O(E log E)

Since E ≤ V² (max possible edges), log(E) ≤ log(V²) = 2·log(V)
— and Big-O drops the constant 2, so log(E) = O(log V) too.

This means O(E log E) and O(E log V) are the SAME Big-O class
— you can write EITHER, they're equivalent.

Plus: initializing current_dist takes O(V) (no log factor,
      just a simple loop)

Total Time = O(V) + O(E log V) = O((V + E) log V)
             [commonly written this way, treating V's log
              factor as harmless since E log V already
              dominates for any connected graph]
'''

import heapq

def dijkstra_standard(graph, source):
    current_dist = {node: float('inf') for node in graph}
    current_dist[source] = 0
    min_heap = [(0, source)]
    finalized = set()
    
    while min_heap:
        dist, node = heapq.heappop(min_heap)
        
        if node in finalized:
            continue
        '''
        when it is popping a node from the heap it has already verified all the possibility
        of reaching that node...if there was any node at any distance smaller than the current
        nodes distance that would have been picked and evaluated, given there were no small route
        in the graph the current node was picked, so once the node is picked/popped, it is sure
        that it's current path is the smallest possible path.

        More precise phrasing: "any UNDISCOVERED path to this node
        would have to pass through SOME other node currently in the
        heap — and since ALL those other nodes have distance >= the
        current smallest, and edge weights can only ADD (never
        subtract, since non-negative), any such undiscovered path
        is GUARANTEED to be >= the current smallest too."
        '''
        finalized.add(node)
        
        for neighbour, weight in graph[node].items():
            if neighbour not in finalized and current_dist[neighbour] > dist + weight:
                current_dist[neighbour] = dist + weight
                heapq.heappush(min_heap, (current_dist[neighbour], neighbour))
    
    return current_dist