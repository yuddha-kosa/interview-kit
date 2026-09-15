class Graph:
    def __init__(self):
        self.adj = {}
    
    def add_node(self, node):
        self.adj[node] = []

    
    def add_edge(self, node1, node2):
        if node1 in self.adj:
            self.adj[node1].append(node2)

        if node2 in self.adj:
            self.adj[node2].append(node1)
    
    def remove_edge(self, node1, node2):
        if node1 in self.adj:
            self.adj[node1].remove(node2)

        if node2 in self.adj:
            self.adj[node2].remove(node1)

class GraphDDW:
    def __init__(self):
        self.adj = {}
    
    def add_node(self, node):
        self.adj[node] = {}

    
    def add_edge(self, node1_from, node2_to, weight):
        if node1_from in self.adj:
            val_dict = self.adj[node1_from]
            val_dict[node2_to] = weight
            self.adj[node1_from] = val_dict

    def remove_edge(self, node1_from, node2_to):
        if node1_from in self.adj:
            val_dict = self.adj[node1_from]
            if node2_to in val_dict:
                del(val_dict[node2_to]) 

class GraphDDW2:
    def __init__(self):
        self.adj = {}
    
    def add_node(self, node):
        self.adj[node] = {}    # a single dict, not a list
    
    def add_edge(self, node1_from, node2_to, weight):
        if node1_from in self.adj:
            self.adj[node1_from][node2_to] = weight   # direct key-value
    
    def remove_edge(self, node1_from, node2_to):
        if node1_from in self.adj and node2_to in self.adj[node1_from]:
            del self.adj[node1_from][node2_to]

class GraphM:
    def __init__(self, num):
        self.n = num
        self.adj_matrix = [[0]*num for _ in range(num)]
        self.node_to_index = {} 
        self.next_index = 0
    
    def add_node(self, node):
        if node not in self.node_to_index:
            self.node_to_index[node] = self.next_index
            self.next_index += 1

    
    def add_edge(self, node1, node2):
        i = self.node_to_index[node1]
        j = self.node_to_index[node2] 
        #if 0 <= node1 < self.n and 0 <= node2 < self.n:
        self.adj_matrix[i][j] = 1
        self.adj_matrix[j][i] = 1
    
    def remove_edge(self, node1, node2):
        i = self.node_to_index[node1]
        j = self.node_to_index[node2] 
        self.adj_matrix[i][j] = 0
        self.adj_matrix[j][i] = 0



class GraphMD:
    def __init__(self, num):
        self.n = num
        self.adj_matrix = [[0]*num for _ in range(num)]
        self.node_to_index = {} 
        self.next_index = 0
    
    def add_node(self, node):
        if node not in self.node_to_index:
            self.node_to_index[node] = self.next_index
            self.next_index += 1

    
    def add_edge(self, node1_from, node2_to, weight):
        i = self.node_to_index[node1_from]
        j = self.node_to_index[node2_to] 
        self.adj_matrix[i][j] = weight
    
    def remove_edge(self, node1_from, node2_to):
        i = self.node_to_index[node1_from]
        j = self.node_to_index[node2_to] 
        self.adj_matrix[i][j] = 0


# 1. Graph -- undirected, unweighted, adjacency LIST
g = Graph()
g.add_node('A'); g.add_node('B'); g.add_node('C')
g.add_edge('A','B')
g.add_edge('A','C')
# g.adj -> {'A': ['B','C'], 'B': ['A'], 'C': ['A']}

# 2. GraphDDW2 -- directed, weighted, adjacency DICT
g = GraphDDW2()
g.add_node('A'); g.add_node('B'); g.add_node('C')
g.add_edge('A','B', 5)
g.add_edge('A','C', 2)
# g.adj -> {'A': {'B':5, 'C':2}, 'B': {}, 'C': {}}

# 3. GraphM -- undirected, unweighted, adjacency MATRIX
g = GraphM(3)   # must specify total node count upfront
g.add_node('A'); g.add_node('B'); g.add_node('C')
g.add_edge('A','B')
# g.adj_matrix -> symmetric matrix, 1 at both [A][B] and [B][A]

# 4. GraphMD -- directed, weighted, adjacency MATRIX
g = GraphMD(3)
g.add_node('A'); g.add_node('B'); g.add_node('C')
g.add_edge('A','B', 7)
# g.adj_matrix -> only [A][B]=7 set, [B][A] stays 0


# ============================================================
# 1. UNDIRECTED + UNWEIGHTED + LIST (adjacency list of lists)
# ============================================================
class UndirectedUnweightedListGraph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        self.adj[node] = []

    def add_edge(self, node1, node2):
        if node1 in self.adj:
            self.adj[node1].append(node2)
        if node2 in self.adj:
            self.adj[node2].append(node1)

    def remove_edge(self, node1, node2):
        if node1 in self.adj:
            self.adj[node1].remove(node2)
        if node2 in self.adj:
            self.adj[node2].remove(node1)


# ============================================================
# 2. DIRECTED + WEIGHTED + MAP (adjacency list of dicts)
# ============================================================
class DirectedWeightedMapGraph:
    def __init__(self):
        self.adj = {}

    def add_node(self, node):
        self.adj[node] = {}

    def add_edge(self, node1_from, node2_to, weight):
        if node1_from in self.adj:
            self.adj[node1_from][node2_to] = weight

    def remove_edge(self, node1_from, node2_to):
        if node1_from in self.adj and node2_to in self.adj[node1_from]:
            del self.adj[node1_from][node2_to]


# ============================================================
# 3. UNDIRECTED + UNWEIGHTED + MATRIX
# ============================================================
class UndirectedUnweightedMatrixGraph:
    def __init__(self, num):
        self.n = num
        self.adj_matrix = [[0]*num for _ in range(num)]
        self.node_to_index = {}
        self.next_index = 0

    def add_node(self, node):
        if node not in self.node_to_index:
            self.node_to_index[node] = self.next_index
            self.next_index += 1

    def add_edge(self, node1, node2):
        i = self.node_to_index[node1]
        j = self.node_to_index[node2]
        self.adj_matrix[i][j] = 1
        self.adj_matrix[j][i] = 1

    def remove_edge(self, node1, node2):
        i = self.node_to_index[node1]
        j = self.node_to_index[node2]
        self.adj_matrix[i][j] = 0
        self.adj_matrix[j][i] = 0


# ============================================================
# 4. DIRECTED + WEIGHTED + MATRIX
# ============================================================
class DirectedWeightedMatrixGraph:
    def __init__(self, num):
        self.n = num
        self.adj_matrix = [[0]*num for _ in range(num)]
        self.node_to_index = {}
        self.next_index = 0

    def add_node(self, node):
        if node not in self.node_to_index:
            self.node_to_index[node] = self.next_index
            self.next_index += 1

    def add_edge(self, node1_from, node2_to, weight):
        i = self.node_to_index[node1_from]
        j = self.node_to_index[node2_to]
        self.adj_matrix[i][j] = weight

    def remove_edge(self, node1_from, node2_to):
        i = self.node_to_index[node1_from]
        j = self.node_to_index[node2_to]
        self.adj_matrix[i][j] = 0

'''
=== UndirectedUnweightedListGraph ===
{'A': ['B', 'C'], 'B': ['A'], 'C': ['A']}

=== DirectedWeightedMapGraph ===
{'A': {'B': 5, 'C': 2}, 'B': {}, 'C': {}}

=== UndirectedUnweightedMatrixGraph ===
node_to_index: {'A': 0, 'B': 1, 'C': 2}
[0, 1, 0]
[1, 0, 0]
[0, 0, 0]

=== DirectedWeightedMatrixGraph ===
node_to_index: {'A': 0, 'B': 1, 'C': 2}
[0, 7, 0]
[0, 0, 0]
[0, 0, 0]
'''