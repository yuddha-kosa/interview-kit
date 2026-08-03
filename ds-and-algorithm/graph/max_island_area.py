from collections import deque

def bfs(grid, visited, start):
    queue = deque()
    queue.append(start)
    visited.add(start)

    area = 1

    while queue:
        i, j = queue.popleft()

        # right
        if i < len(grid) and j+1 < len(grid[0]) and (i, j+1) not in visited and grid[i][j+1] != "0":
            area += 1
            visited.add((i, j+1))
            queue.append((i, j+1))

        # left
        if i < len(grid) and j-1>= 0 and (i, j-1) not in visited and grid[i][j-1] != "0":
            area += 1
            visited.add((i, j-1))
            queue.append((i, j-1))

        # bottom
        if i+1 < len(grid) and j < len(grid[0]) and (i+1, j) not in visited and grid[i+1][j] != "0":
            area += 1
            visited.add((i+1, j))
            queue.append((i+1, j))

        # top
        if i-1 >= 0 and j < len(grid[0]) and (i-1, j) not in visited and grid[i-1][j] != "0":
            area += 1
            visited.add((i-1, j))
            queue.append((i-1, j))
    return area
        
def cal_area(grid, visited, start):
    i, j = start
    area = 0
    def dfs(grid, visited, i, j):
        nonlocal area
        if i < 0 or j < 0 or i > len(grid)-1 or j > len(grid[0])-1 or grid[i][j] == "0" or (i, j) in visited:
            return
        area += 1
        visited.add((i,j))
        dfs(grid, visited, i+1, j)  
        dfs(grid, visited, i-1, j)  
        dfs(grid, visited, i, j+1)  
        dfs(grid, visited, i, j-1)  
    dfs(grid, visited, i, j)
    return area


def largest_area(grid):

    max_area = 0
    visited = set()

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] != "0":
                if (i,j) not in visited:
                    #area = bfs(grid, visited, (i,j))
                    area = cal_area(grid, visited, (i,j))
                    max_area = max(max_area, area)
            else:
                visited.add((i,j))

    return max_area
                     


grid = [
  ["1","1","0","0"],
  ["1","1","0","0"],
  ["0","0","1","0"],
  ["0","0","0","1"]
]

print(largest_area(grid))


'''
Time:  O(rows × cols)
Space: O(rows × cols)
'''