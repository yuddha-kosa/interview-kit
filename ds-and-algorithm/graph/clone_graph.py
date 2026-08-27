
from collections import deque

class Graph:
    def __init__(self):
        self.adj = {}
    
    def insertNode(self, val):
        self.adj[val] = []
    
    def insertEdges(self, node1, node2):
        if node1 in self.adj:
            self.adj[node1].append(node2)

def clone_graph(root):
    graph = Graph()

    queue = deque()
    queue.append(1)
    visited = set()
    visited.add(1)

    while queue:
        node = queue.pop()

        graph.insertNode(node)

        nodes_list = root[node-1]
        for n in nodes_list:
            graph.insertEdges(node, n)
            if n not in visited:
                visited.add(n)
                queue.append(n)
    return graph.adj



print(clone_graph([[2,4], [1,3], [2,4], [1,3]]))

'''
Time:  O(V + E) — every node and edge processed once
Space: O(V + E) — new graph structure + visited set
'''

class Node:
    def __init__(self, val=0, neighbors=None):
        self.val = val
        self.neighbors = neighbors if neighbors else []
def clone_graph1(root):
    cloned_nodes = {}

    def dfs(node):
        if node in cloned_nodes:
            return cloned_nodes[node]
        clone_node = Node(node.val)
        cloned_nodes[node] = clone_node

        for adj_node in node.neighbors:
            adj_clone = dfs(adj_node)
            clone_node.neighbors.append(adj_clone)
        return clone_node
    
    return dfs(root)

'''
Time:  O(V + E) — every node and edge visited once
Space: O(V) — cloned_nodes map + recursion depth
'''