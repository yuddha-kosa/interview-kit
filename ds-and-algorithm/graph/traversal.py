from collections import deque


def dfs(graph, start):
    if start not in graph:
        return
    result = []
    visited = set([start])

    stackq = deque()
    stackq.append(start)

    while stackq:
        vertex = stackq.pop()
        result.append(vertex)
        for v in graph[vertex]:
            if v not in visited:
                visited.add(v)
                stackq.append(v)
    
    return result

def bfs(graph, start):
    if start not in graph:
        return
    result = []
    visited = set([start])
    queue = deque()
    queue.append(start)

    while queue:
        vertex = queue.popleft() 
        result.append(vertex)
        for neighbour in graph[vertex]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return result

graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}
print(dfs(graph, "A"))
print(bfs(graph, "A"))