from collections import deque

def detect_cycle(graph, start):

    visited = set()
    queue = deque()
    queue.append((start, None))
    visited.add(start)


    while queue:
        node, parent = queue.pop()

        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append((neighbour, node))
            else:
                if neighbour != parent:
                    return True
    return False


graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}
print(detect_cycle(graph, 'A'))

graph_no_cycle = {
    'D': ['E'],
    'E': ['D']
}
print(detect_cycle(graph_no_cycle, 'D'))

'''
Time:  O(V + E)
Space: O(V) — visited set + stack
'''

'''
cycle detetion:

The rule is really about the EDGE, not about WHEN you visit
things: "if I can reach an ALREADY-VISITED node through an
edge that ISN'T the one I just came from, that means there
are TWO DIFFERENT PATHS to that node — which is EXACTLY what
a cycle is."

This is a STRUCTURAL property of the graph itself — it doesn't
change based on whether you explore BREADTH-first or DEPTH-first.
The ONLY requirement (which you already identified and fixed)
is that each node must correctly know its OWN parent, regardless
of which traversal strategy delivers that information.
'''


def has_cycle_undirected(graph):
    visited = set()
    def dfs(node, parent):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                if dfs(neighbor, node): # if false (cycle not detected) check more depth, if cycle detected return immediately
                    return True
            elif neighbor != parent:
                return True
        return False
    
    for node in graph:              # handles DISCONNECTED components
        if node not in visited:
            if dfs(node, None):
                return True
    return False