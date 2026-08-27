from collections import deque
'''
def dfs1(start, graph, visited):
    stack = deque()
    stack.append((start, None))

    while stack:
        node, parent = stack.pop()
        print(f"node: {node}, parent: {parent}")
        visited.add(node)

        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                stack.append((neighbour, node))
            else:
                print(f"neighbour in visited: {neighbour}, parent: {parent}")
                if neighbour != parent:
                    return [node, neighbour]
    return []


def find_redundant_connection1(edges, n):
    graph = {}
    for src, dst in edges:
        if src not in graph:
            graph[src] = []
        graph[src].append(dst)
        if dst not in graph:
            graph[dst] = []
        graph[dst].append(src)
    
    print(graph)
    visited = set()
    result = []
    for vertex in graph:
        if vertex not in visited:
            result.append(dfs1(vertex, graph, visited))
    return result
'''

def dfs(graph, src, dst, visited):
    if src == dst:
        return True
    visited.add(src)
    for neighbour in graph.get(src, []):
        if neighbour not in visited:
            if dfs(graph, neighbour, dst, visited):
                return True
    return False




def find_redundant_connection(edges, n):
    graph = {}

    for src, dst in edges:
        visited = set()
        resp = dfs(graph, src, dst, visited)
        if src in graph and dst in graph and resp:
            return [src, dst]
        
        if src not in graph:
            graph[src] = []
        graph[src].append(dst)

        if dst not in graph:
            graph[dst] = []
        graph[dst].append(src)



print(find_redundant_connection([[1,2], [1,3], [2,3]], 3))


def find_redundant_connection_uf(edges, n):
    parent = list(range(n+1))
    rank = [0]*(n+1)

    print("parent: ", parent)
    print("rank: ", rank)

    def find(node):
        if parent[node] == node:
            return node
        parent[node] = find(parent[node])
        return parent[node]
    def union(u, v):
        u_root = find(u)
        v_root = find(v)
        if u_root == v_root:
            return True
        
        if rank[u_root] > rank[v_root]:
            parent[v_root] = u_root
        else:
            parent[u_root] = v_root
            if rank[u_root] == rank[v_root]:
                rank[v_root] += 1
        return False
    
    for src, dst in edges:
        #print("parent: ", parent)
        if union(src, dst):
            #print(f"edge: {src, dst}, res: {res}")
            return [src, dst]
    return []
        

print(find_redundant_connection_uf([[1,2], [1,3], [2,3]], 3))

def find_redundant_connection_general(edges):
    # Step 1: collect all UNIQUE node labels that actually appear
    all_nodes = set()
    for u, v in edges:
        all_nodes.add(u)
        all_nodes.add(v)
    
    # Step 2: map each label to a compact index (0, 1, 2...)
    label_to_index = {label: i for i, label in enumerate(all_nodes)}
    n = len(all_nodes)
    
    parent = list(range(n))
    rank = [0]*n
    
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[rx] = ry
            if rank[rx] == rank[ry]:
                rank[ry] += 1
        return True
    
    for u, v in edges:
        iu, iv = label_to_index[u], label_to_index[v]
        if not union(iu, iv):
            return [u, v]
    return []