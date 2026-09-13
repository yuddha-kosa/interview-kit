'''
PROBLEM: Autonomous Racing Car Navigation

You are developing a navigation algorithm for an autonomous 
racing car on a grid-based test track. The track is represented 
as a 2D matrix of size N x M.

The matrix contains different types of tiles:
- 'S': The unique Starting Position of the racing car.
- '.': Open asphalt tracks where the car can travel freely.
- 'X': Obstacles, walls, or off-track zones where the car 
       cannot travel.
- 'F': A Target Flag checkpoint. There can be multiple flags 
       placed across the track.

The racing car can move from its current cell to any adjacent 
cell in the four cardinal directions (Up, Down, Left, Right), 
provided the target cell is within the grid boundaries and is 
not an obstacle ('X'). Each movement between adjacent cells 
takes exactly 1 second (unweighted edges).

TASK:
Analyze the track and find the total number of unique, optimal 
(shortest-time) paths from the starting position 'S' to any of 
the reachable flags 'F'.

An optimal path to a flag is defined as a path that reaches 
that specific flag in the absolute minimum possible time. If 
multiple distinct flags can be reached in that same minimum 
time, their unique path counts should be summed together. If 
no flags are reachable from the starting position, return 0.
'''
from collections import deque

def race_track_flag_finder(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    
    # 1. Initialize Distance Tracker (Infinity) and Path Tracker (Zeros)
    dist = [[float('inf')] * cols for _ in range(rows)]
    paths = [[0] * cols for _ in range(rows)]
    
    start_r, start_c = 0, 0
    flags = []
    
    # 2. Map coordinates for Start and Flags
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 'S':
                start_r, start_c = r, c
            elif matrix[r][c] == 'F':
                flags.append((r, c))
                
    # 3. Setup BFS Queue
    queue = deque([(start_r, start_c)])
    dist[start_r][start_c] = 0
    paths[start_r][start_c] = 1
    
    # 4. Level-Order Traversal
    while queue:
        r, c = queue.popleft()
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            
            # Boundary and Obstacle Isolation Check
            if 0 <= nr < rows and 0 <= nc < cols and matrix[nr][nc] != 'X':
                new_dist = dist[r][c] + 1
                
                # Case A: Found a brand new shorter path to this cell
                if new_dist < dist[nr][nc]:
                    dist[nr][nc] = new_dist
                    paths[nr][nc] = paths[r][c]  # Inherit path counts
                    queue.append((nr, nc))
                    
                # Case B: Found an alternative optimal path to this cell
                elif new_dist == dist[nr][nc]:
                    paths[nr][nc] += paths[r][c]  # Accumulate DP combinations
                    
    # 5. Extract global minimum distance to any flag
    min_flag_dist = min([dist[fr][fc] for fr, fc in flags])
    
    if min_flag_dist == float('inf'):
        return 0
        
    # Sum up paths of all flags that share that absolute optimal distance
    total_optimal_paths = sum([paths[fr][fc] for fr, fc in flags if dist[fr][fc] == min_flag_dist])
    
    return total_optimal_paths
