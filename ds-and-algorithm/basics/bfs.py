from collections import deque

def bfs(graph, start):
    queue = deque(start)
    #print(f"queue: {queue}")
    visited = set(start)

    while queue:
        node = queue.popleft()
        #print(f"queue: {queue}")
        print(f"{node}")
        for neighbours in graph[node]:
            if neighbours not in visited:
                visited.add(neighbours)
                queue.append(neighbours)
                #print(f"queue: {queue}")

    print(f"visited: {visited}")



graph = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["F"],
    "D": [], "E": [], "F": []
}

bfs(graph, "A")    # A B C D E F