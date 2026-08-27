def find_path(grid, start, path_exist):
    i, j = start
    prev = grid[i][j]

    def dfs(i, j, grid, path_exist, prev):
        if i > len(grid)-1 or i < 0 or j > len(grid[0])-1 or j < 0 or (i,j) in path_exist or grid[i][j] < prev:
            return
        
        path_exist.add((i,j))

        prev = grid[i][j] 

        dfs(i+1, j, grid, path_exist, prev)
        dfs(i-1, j, grid, path_exist, prev)
        dfs(i, j-1, grid, path_exist, prev)
        dfs(i, j+1, grid, path_exist, prev)
    dfs(i,j, grid, path_exist, prev)


def pacific_atlantic(grid):
    pacific = set()
    atlantic = set()
    pacific_path_exist = set()
    atlantic_path_exist = set()
    for j in range(len(grid[0])):
        pacific.add((0,j)) 
        atlantic.add((len(grid)-1,j))
    for i in range(len(grid)):
        pacific.add((i,0)) 
        atlantic.add((i,(len(grid[0])-1))) 

    # pacific
    for point in pacific:
        find_path(grid, point, pacific_path_exist)
    for point in atlantic:
        find_path(grid, point, atlantic_path_exist)
    return list(pacific_path_exist & atlantic_path_exist)



grid = [
    [1,2,2,3,5],
    [3,2,3,4,4],
    [2,4,5,3,1],
    [6,7,1,4,5],
    [5,1,1,2,4]
]

print(pacific_atlantic(grid))
'''
pacific:
0-(0-4)
1-(0-3)
2-(0-2)
3-(0-1)
4-(0-0)

atlantic:
0-(4-4)
1-(3-4)
2-(2-4)
3-(1-4)
4-(0-4)

'''