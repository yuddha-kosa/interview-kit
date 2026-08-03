def longest_increasing_path(grid):
    max_len = 0
    mem = {}
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            curr_len = dfs(i,j,-float('inf'), grid, mem)
            if curr_len > max_len:
                max_len = curr_len
    return max_len

def dfs(i, j, prev, grid, mem):
    if i < 0 or j < 0:
        return 0
    if i >= len(grid) or j >= len(grid[0]):
        return 0
    if grid[i][j] <= prev:
        return 0

    if (i,j) in mem:
        return mem[(i,j)]

    d = dfs(i+1, j, grid[i][j], grid, mem)
    r = dfs(i, j+1, grid[i][j], grid, mem)
    u = dfs(i-1, j, grid[i][j], grid, mem)
    l = dfs(i, j-1, grid[i][j], grid, mem)
    max_len = 1 + max(d, r, u, l)
    mem[(i,j)] = max_len
    return max_len

grid = [[9,9,4],
        [6,6,8],
        [2,1,1]]

print(longest_increasing_path(grid))


# can it be solved with tabular ?? TBD Discuss tomorrow... and time complexity...
# Time complexity = O(mn × 4^(mn))
# Space = O(m*n)

'''
level 0: 1  = 4^0   ✓
level 1: 4  = 4^1   ✓
level 2: 16 = 4^2   ✓
level 3: 64 = 4^3   ✓
level n: should be 4^n,


level n = 4^n nodes

Total nodes summed across levels 0 to D (D = max depth = mn):
Total = 4^0 + 4^1 + 4^2 + ... + 4^D
      = (4^(D+1) - 1) / 3
      ≈ O(4^D)
      = O(4^(mn))

General geometric series formula:
a + ar + ar² + ... + ar^n = a × (r^(n+1) - 1) / (r - 1)

For your case — a=1, r=4:
4^0 + 4^1 + 4^2 + ... + 4^D = (4^(D+1) - 1) / (4 - 1)
                              = (4^(D+1) - 1) / 3

'''