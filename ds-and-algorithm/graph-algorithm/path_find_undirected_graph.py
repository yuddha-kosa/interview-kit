
from collections import deque

def has_path(graph, source, destination):
    path = []
    path.append(source)
    queue = deque()
    queue.append((source, path))

    visited = set()
    visited.add(source)

    while queue:
        node, path = queue.popleft()


        if node == destination:
            print("path:", path)
            return True

        for neighbour in graph[node]:
            if neighbour not in visited:
                visited.add(neighbour)
                '''
                The `+` operator on lists creates a BRAND NEW list (a
                combination of the two), leaving the ORIGINAL `path` list
                COMPLETELY UNTOUCHED. Every branch gets its OWN independent
                copy — no shared mutable state, no corruption between
                different exploration paths.
                '''
                queue.append((neighbour, path+[neighbour])) 
                #queue.append((neighbour, path.append(neighbour))) 
    return False 


graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A'],
    'D': ['B'],
    'X': ['Y'],
    'Y': ['X']
}

print(has_path(graph, 'A', 'D'))   # expect True  (A-B-D)
print(has_path(graph, 'C', 'D'))   # expect True  (C-A-B-D)
print(has_path(graph, 'A', 'X'))   # expect False (completely disconnected)
print(has_path(graph, 'A', 'A'))   # expect True  (same node — trivial path)
print(has_path(graph, 'X', 'Y'))   # expect True  (direct edge)

'''
Time:  O(V + E)
Space: O(V)
'''

'''
This works for both directed and undirected graphs.
'''