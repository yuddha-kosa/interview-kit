def rotate_matrix(matrix):
    n = len(matrix)
    for i in range(n):
        for j in range(i+1, n):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    
    for i in range(n):
        l = n-1
        for j in range(n):
            if j < l:
                matrix[i][j], matrix[i][l] = matrix[i][l], matrix[i][j]
            else:
                break
            l -= 1
    return matrix

print(rotate_matrix([[1,2], [3,4]]))
print(rotate_matrix([[10,11,12,13], [14,15,16,17], [18,19,20,21], [22,23,24,25]]))