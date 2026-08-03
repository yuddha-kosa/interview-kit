
def toeplitz_matrix(matrix):

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows-1, -1,-1):
        for j in range(cols):
            if i+1 < rows and j+1 < cols and matrix[i][j] != matrix[i+1][j+1]:
                return False
    
    return True

print(toeplitz_matrix([[2,3,4,5], [6,2,3,4], [9,6,2,3]]))
print(toeplitz_matrix([[7,8], [6,7], [5,6]]))
'''
Matrix:
1 2 3
4 1 2
5 4 1
'''

def toeplitz_matrix2(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    for i in range(rows - 1):
        for j in range(cols - 1):
            if matrix[i][j] != matrix[i+1][j+1]:
                return False
    return True