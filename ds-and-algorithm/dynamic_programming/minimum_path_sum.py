def min_path_sum(grid):
    min_path_sum = float('inf') 
    path = []
    def backtrack(i,j):
        nonlocal min_path_sum 
        if i == len(grid) or j == len(grid[0]): 
            return

        path.append(grid[i][j])

        if i == len(grid)-1 and j == len(grid[0])-1:
            min_path_sum = min(min_path_sum, sum(path[:]))
            path.pop()
            return
        
        backtrack(i, j+1)
        backtrack(i+1, j)
        path.pop()

    backtrack(0,0)
    return min_path_sum




grid = [[1,3,1],
        [1,5,1],
        [4,2,1]]
print(min_path_sum(grid))


def min_path_sum1(grid):
    result = float('inf')
    path = []
    def backtrack(i, j):
        nonlocal result
        if i == len(grid) or j == len(grid[0]):
            return
        path.append(grid[i][j])
        if i == len(grid)-1 and j == len(grid[0])-1:
            result = min(result, sum(path))
        else:
            backtrack(i, j+1)
            backtrack(i+1, j)
        path.pop()
    backtrack(0, 0)
    return result

grid = [[1,3,1],
        [1,5,1],
        [4,2,1]]
print(min_path_sum1(grid))   # 7



# table is storing the smallest path to reach any point i,j...so for every point i,j we will have
# the shortest way to reach it and the last i, j(-1,-1) will give us our desired destination.
def min_path_sum_dp(grid):
    table = [[0 for _ in range(len(grid[0]))] for _ in range(len(grid))]
    table[0][0] = grid[0][0]

    # base cases
    # 1. there is only one way to reach all the 1st row and all columns..just one after the another.
    for j in range(1, len(grid[0])):
        table[0][j] = table[0][j-1] + grid[0][j]

    # 2. there is only one way to reach all the 1st columns and all the rows..just one after the another.
    for i in range(1, len(grid)):
        table[i][0] = table[i-1][0] + grid[i][0]
    
    for i in range(1, len(grid)):
        for j in range(1, len(grid[0])):
            table[i][j] = min(table[i][j-1], table[i-1][j]) + grid[i][j]
    
    return table[-1][-1]

grid = [[1,3,1],
        [1,5,1],
        [4,2,1]]
print(min_path_sum_dp(grid))   # 7