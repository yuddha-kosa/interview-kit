import heapq

def prims(graph):
    start = ''
    for k in graph.keys():
        start = k
        break

    heap = [(0, start, None)]
    visited = set()
    tree = {}
    weight = 0

    while heap:
        dist, node, parent = heapq.heappop(heap)

        if node in visited:
            continue
        visited.add(node)
        weight += dist

        # create tree
        if parent:
            if parent not in tree:
                tree[parent] = []
            tree[parent].append((node, dist))


        for neigh, wt in graph.get(node, []):
            if neigh not in visited:
                heapq.heappush(heap, (wt, neigh, node))
    print("Tree: ", tree) 
    return weight

graph1 = {
    'A': [('B',4), ('C',1)],
    'B': [('A',4), ('C',2), ('D',5)],
    'C': [('A',1), ('B',2), ('D',8)],
    'D': [('B',5), ('C',8)]
}
# Expected MST edges: A-C(1), C-B(2), B-D(5), total weight = 8
print(prims(graph1))

graph2 = {
    'A': [('B',1), ('C',2)],
    'B': [('A',1), ('C',2), ('D',1)],
    'C': [('A',2), ('B',2), ('D',1)],
    'D': [('B',1), ('C',1)]
}
# Expected MST: A-B(1), B-D(1), D-C(1), total weight = 3
print(prims(graph2))

'''
Time:  O(E log V)
Space: O(V + E)
'''