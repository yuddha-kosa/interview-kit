def set_matrix_zeroes(matrix):

    row_group = set()
    col_group = set()

    row = len(matrix)
    col = len(matrix[0])
    for i in range(row):
        for j in range(col):
            if matrix[i][j] == 0:
                row_group.add(i)
                col_group.add(j)
    for i in row_group:
        for j in range(col):
            matrix[i][j] = 0

    for j in col_group:
        for i in range(row):
            matrix[i][j] = 0
    return matrix

print(set_matrix_zeroes([[2,2,2],[2,0,2], [2,2,2]]))
print(set_matrix_zeroes([[0,3,4,0],[1,2,5,6], [7,8,9,10]]))

def set_matrix_zeroes1(matrix):
    rows = len(matrix)
    cols = len(matrix[0])

    # check if first row and col have zeros
    first_row_zero = any(matrix[0][j] == 0 for j in range(cols))
    first_col_zero = any(matrix[i][0] == 0 for i in range(rows))

    # use first row and col as markers
    for i in range(1, rows):
        for j in range(1, cols):
            if matrix[i][j] == 0:
                matrix[i][0] = 0    # mark row
                matrix[0][j] = 0    # mark col

    # zero out marked rows and cols
    for i in range(1, rows):
        for j in range(1, cols):
            if matrix[i][0] == 0 or matrix[0][j] == 0:
                matrix[i][j] = 0

    # handle first row
    if first_row_zero:
        for j in range(cols):
            matrix[0][j] = 0

    # handle first col
    if first_col_zero:
        for i in range(rows):
            matrix[i][0] = 0

    return matrix