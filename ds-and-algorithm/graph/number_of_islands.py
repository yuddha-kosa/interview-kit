from collections import deque

def bfs(grid, visited, start):
    queue = deque()
    queue.append(start)
    visited.add(start)

    while queue:
        i, j = queue.popleft()

        # right
        if i < len(grid) and j+1 < len(grid[0]) and (i, j+1) not in visited and grid[i][j+1] != "0":
            visited.add((i, j+1))
            queue.append((i, j+1))

        # left
        if i < len(grid) and j-1>= 0 and (i, j-1) not in visited and grid[i][j-1] != "0":
            visited.add((i, j-1))
            queue.append((i, j-1))

        # bottom
        if i+1 < len(grid) and j < len(grid[0]) and (i+1, j) not in visited and grid[i+1][j] != "0":
            visited.add((i+1, j))
            queue.append((i+1, j))

        # top
        if i-1 >= 0 and j < len(grid[0]) and (i-1, j) not in visited and grid[i-1][j] != "0":
            visited.add((i-1, j))
            queue.append((i-1, j))
        


def num_islands(grid):

    num = 0
    visited = set()

    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] != "0":
                if (i,j) not in visited:
                    num += 1
                    bfs(grid, visited, (i,j))
            else:
                visited.add((i,j))

    return num
                     


grid = [
  ["1","1","0","0"],
  ["1","1","0","0"],
  ["0","0","1","0"],
  ["0","0","0","1"]
]

print(num_islands(grid))


'''
Time:  O(rows × cols)
Space: O(rows × cols)
'''

'''
 num = 0

    rows = len(grid)-1
    cols = len(grid[0])-1
    i= 0
    j= 0
    visited = set()

    while i <= rows and j <= cols:

        if grid[i][j] != 0:
            if (i,j) not in visited:
                num += 1
                bfs(grid, visited, (i,j))
        else:
            visited.add((i,j))
'''