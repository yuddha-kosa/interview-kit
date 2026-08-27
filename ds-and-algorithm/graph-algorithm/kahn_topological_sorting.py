
from collections import deque
def kahntopologicalsorting(graph, v):
    '''
    indegree = [0]*v
    for vertex in graph:
        for neighbour in vertex:
            indegree[neighbour] += 1
    '''
    indegree = {}
    for vertex in graph:
        if vertex not in indegree:
            indegree[vertex] = 0 
        for neighbour in graph[vertex]:
            indegree[neighbour] = indegree.get(neighbour, 0) + 1

    queue = deque()

    for neigh, deg in indegree.items():
        if deg == 0:
            queue.append(neigh) 
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)

        for neig in graph[node]:
            indegree[neig] -= 1 
            if indegree[neig] == 0:
               queue.append(neig) 
    
    if len(result) != v:
        return "cycle detected"
    return result


graph1 = {'A':['B','C'], 'B':['D'], 'C':['D'], 'D':[]}
print(kahntopologicalsorting(graph1, 4))
# Expected: some valid order like ['A','B','C','D'] or ['A','C','B','D']

'''
Time:  O(V+E)
Space: O(V+E)
'''
'''
A- {B, C} B- {D} C- {D} D- {F} E- {B,F} F- {}

In this graph there is no cycle

A→B, A→C, B→D, B→E, C→D, D→F, E→F

In-degrees:

    A: 0   (nothing points to A)

    B: 2   (A points to B and E points to B)

    C: 1   (A points to C)

    D: 2   (B and C both point to D)

    E: 0   (E points to B and F)

    F: 2   (D and E both point to F)

'''