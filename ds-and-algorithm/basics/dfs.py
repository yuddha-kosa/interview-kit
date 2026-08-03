from collections import deque

def dfs(graph, start):
    stack = deque(start) #treat it as a stack.
    visited = set(start)

    while stack:
        node = stack.pop()
        print(f"{node}")
        for child in graph[node]:
            if child not in visited:
                visited.add(child)
                stack.append(child)
    print(f"visited: {visited}")


graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [], "E": [], "F": []
}

dfs(graph, "A")    # A B C D E F
# A C F B E D