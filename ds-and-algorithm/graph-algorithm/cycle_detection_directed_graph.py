
def cycle_detection(graph):
    visited = set()
    recursion_stack = set()

    def dfs(node):
        visited.add(node)
        recursion_stack.add(node)

        for neighbour in graph[node]:
            if neighbour not in visited:
                if dfs(neighbour): # if false check more depth, if cycle detected return immediately
                    return True
            elif neighbour in recursion_stack:
                return True
        recursion_stack.remove(node)
        return False


    for node in graph:
        if node not in visited:
            if dfs(node):
                return True
    return False

graph1 = {'A': ['B'], 'B': ['C'], 'C': ['A']}
# A → B → C → A
# Expected: True

graph2 = {'A': ['B', 'C'], 'B': ['C'], 'C': []}
# A → B → C, and A → C directly
# Expected: False

graph3 = {'A': ['B', 'C'], 'B': ['A', 'C'], 'C': []}
# A → B, B → A (this alone is a cycle)
# Expected: True

graph4 = {'A': ['A']}
# A points to itself
# Expected: True

graph5 = {'A': ['B'], 'B': ['C'], 'C': []}
# Expected: False

print(cycle_detection(graph1))
print(cycle_detection(graph2))
print(cycle_detection(graph3))
print(cycle_detection(graph4))
print(cycle_detection(graph5))