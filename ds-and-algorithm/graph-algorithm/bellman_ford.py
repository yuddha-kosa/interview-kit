from collections import deque

def bellmanford(graph, source):
    current_dist = {}
    for node in graph:
        if node == source:
            current_dist[node] = 0
        else:
            current_dist[node] = float('inf')

    for round in range(len(graph)-1):
        queue =  deque()
        queue.append((0, source))

        visited = set()

        while queue:
            dist, node = queue.popleft()
            visited.add(node)
            for neighbour, weight in graph[node].items():
                c_weight = dist+weight
                #print(f"round: {round}, node: {node}, neighbour: {neighbour}, current_weight: {current_dist[neighbour]}, new_weight: {c_weight}")
                if current_dist[neighbour] > c_weight:
                    current_dist[neighbour] = c_weight
                if neighbour not in visited:
                    queue.append((current_dist[neighbour], neighbour))
        #print(f"round: {round}, current_dict: {current_dist}")

    for vertex in graph:
        for neighbour, weight in graph[vertex].items():
            if current_dist[neighbour] > current_dist[vertex]+weight:
                return "Negative cycle detected"


    return current_dist



vertices1 = ['A', 'B', 'C']
graph1 = {
    'A': {'B': 2, 'C': 5},
    'B': {},
    'C': {'B': -10}
}
# Expected: A=0, B=-5, C=5

vertices2 = ['A','B','C','D','E']
graph2 = {
    'A': {'B': 4, 'C': 2},
    'B': {'D': 2, 'E': 3},
    'C': {'B': -3, 'D': 5},
    'D': {'E': -1},
    'E': {}
}
# Expected: A=0, B=-1, C=2, D=1, E=0

vertices3 = ['A', 'B', 'C']
graph3 = {
    'A': {'B': 1},
    'B': {'C': -1},
    'C': {'B': -1}    # B->C->B keeps decreasing forever: -1 + -1 = -2 per loop
}
# After V-1 rounds, run ONE MORE round: if ANYTHING still improves,
# that confirms a negative cycle exists (no finite shortest path)

vertices4 = ['A', 'B', 'C', 'D']
graph4 = {
    'A': {'B': 1, 'C': 4},
    'B': {'C': 2, 'D': 5},
    'C': {'D': 1},
    'D': {}
}
# Expected: A=0, B=1, C=3, D=4

print(bellmanford(graph1, "A"))
print(bellmanford(graph2, "A"))
print(bellmanford(graph3, "A"))
print(bellmanford(graph4, "A"))

'''
time: O(V × (V+E))
space: O(V + E)
'''

def bellman_ford_with_detection(graph, source, vertices):
    dist = {v: float('inf') for v in vertices}
    dist[source] = 0
    edges = [(u, v, w) for u in graph for v, w in graph[u].items()]
    
    V = len(vertices)
    for _ in range(V - 1):
        for u, v, w in edges:
            if dist[u] != float('inf') and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    
    # ONE EXTRA round -- just to CHECK, not apply
    for u, v, w in edges:
        if dist[u] != float('inf') and dist[u] + w < dist[v]:
            return "Negative cycle detected"
    
    return dist


def bellman_ford_with_detection1(graph, start):
    dist = {vert: float('inf') for vert in graph}
    dist[start] = 0
    
    for _ in range(len(graph)-1):
        for vertex in graph:
            for neighbour, wt in graph[vertex]:
                if dist[neighbour] > dist[vertex] + wt:
                    dist[neighbour] = dist[vertex] + wt

    for vertex in graph:
        for neighbour, wt in graph[vertex]:
                if dist[neighbour] > dist[vertex] + wt:
                    return "negative cycle"
    
    return dist



'''
time: O(VE))
space: O(V+E)
'''