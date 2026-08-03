def diagonal_sum(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    seen = set()
    sum = 0
    for i in range(rows):
        sum += matrix[i][i]
        #print(f"matrix[i][i]: {matrix[i][i]}")
        seen.add(matrix[i][i])
        #if matrix[i][cols-1-i] not in seen:
        if i != cols - 1 - i:
            #print(f"other diag: {matrix[i][cols-1-i]}")
            sum += matrix[i][cols-1-i]
    return sum

print(diagonal_sum([[1,2,3], [4,5,6], [7,8,9]]))
print(diagonal_sum([[2,2,2,2], [2,2,2,2], [2,2,2,2], [2,2,2,2]]))
