
def dfs(vertex, graph, visited, stack):
    visited.add(vertex)

    for neighbour in graph[vertex]:
        if neighbour not in visited:
            dfs(neighbour, graph, visited, stack)
    
    stack.append(vertex)


def dfstopologicalsorting(graph):
    visited = set()
    stack = []

    for vertex in graph:
        if vertex not in visited:
            dfs(vertex, graph, visited, stack)
    return stack[::-1]