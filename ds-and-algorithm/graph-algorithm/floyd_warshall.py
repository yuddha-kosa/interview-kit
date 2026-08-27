
def floyd_warshall(weight):

    size = len(weight)
    for k in range(size): # pass all the path from each vertex once. 
        # for each vetext i to all the vertext j through k.
        for i in range(size): 
            for j in range(size):
                if weight[i][k] + weight[k][j] < weight[i][j]:
                    weight[i][j] = weight[i][k] + weight[k][j] 
    return weight


dist = [
    [0,   3,  10, float('inf'), float('inf')],
    [float('inf'), 0, float('inf'), 2, float('inf')],
    [float('inf'), float('inf'), 0, 1, 8],
    [float('inf'), float('inf'), float('inf'), 0, 4],
    [float('inf'), float('inf'), float('inf'), float('inf'), 0]
]

print(floyd_warshall(dist))

INF = float('inf')
graph = [
    [0,   3,   8,   INF, -4],
    [INF, 0,   INF, 1,   7],
    [INF, 4,   0,   INF, INF],
    [2,   INF, -5,  0,   INF],
    [INF, INF, INF, 6,   0]
]

print(floyd_warshall(graph))

'''
Time:  O(V³) — three nested loops, each O(V)
Space: O(1) extra (modifies the matrix IN PLACE) — or O(V²)
       if you count the input matrix itself
'''

def convert_to_matrix(edges):


edges = [
    ("A", "B", 3),
    ("A", "C", 10),
    ("B", "D", 2),
    ("C", "D", 1),
    ("C", "E", 8),
    ("D", "E", 4)
]

print(convert_to_matrix(edges))