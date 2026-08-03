from collections import defaultdict

def diagonal_sorting(matrix):
    pairs = defaultdict(list)
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows):
        for j in range(cols):
            pairs[i-j].append(matrix[i][j])
    
    for key in pairs.keys():
        pairs[key].sort()

    for d, vals in pairs.items():
        if d >= 0:
            start_row = d
            start_col = 0
        else:
            start_row = 0
            start_col = -d
        for i, val in enumerate(vals):
            matrix[start_row+i][start_col+i] = val
    return matrix


        

print(diagonal_sorting([[3,3,1,1], [2,2,1,2], [1,1,1,2]]))