def fill_color(image, start, color, visited):
    i, j = start
    original_col = image[i][j]
    def dfs(i, j, image):
        if i > len(image)-1 or i < 0 or j > len(image[0])-1 or j < 0 or (i,j) in visited or image[i][j] != original_col:
            return
        image[i][j] = color
        visited.add((i,j))

        dfs(i+1, j, image)
        dfs(i-1, j, image)
        dfs(i, j-1, image)
        dfs(i, j+1, image)
    dfs(i,j, image)

def flood_fill(image, sr, sc, color):

    visited = set()

    fill_color(image, (sr,sc), color, visited)
    return image


image = [[1,1,1],
         [1,1,0],
         [1,0,1]]
sr=1
sc=1
newColor=2
print(flood_fill(image, sr, sc, newColor))

image = [[0,0,0],
         [0,0,0]]
sr=0
sc=0
newColor=0
print(flood_fill(image, sr, sc, newColor))


'''
Time:  O(rows × cols)
Space: O(rows × cols) — visited set + recursion depth
'''