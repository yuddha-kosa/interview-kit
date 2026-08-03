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