def spiral_matrix(matrix):
    top = 0
    bottom = len(matrix)-1
    left = 0
    right = len(matrix[0])-1

    result = []

    while top <= bottom and left <= right:
        for i in range(left, right+1): # include the right most
            result.append(matrix[top][i])
        top += 1

        for j in range(top, bottom+1):
            result.append(matrix[j][right]) # right most excluded, included the bottom
        right -= 1

        if top <= bottom:  # guard — not single row 
            for k in range(right, left-1, -1):
                #print(f"bottom: {bottom}, k: {k}")
                result.append(matrix[bottom][k]) # include the left most and exclude the bottom right
            bottom -= 1

        if left <= right: # guard — not single col
            for l in range(bottom, top-1, -1):
                #print(f"l: {l}, left: {left}")
                result.append(matrix[l][left]) # exclude the bottom left and include the top most
            left += 1

    return result




print(spiral_matrix([[1,2,3,4],[8,7,6,5],[9,10,11,12], [13,14,15,16]]))
print(spiral_matrix([[1,2,3], [6,5,4], [7,8,9]]))
print(spiral_matrix([[1,2,3]]))
print(spiral_matrix([[1,2,3], [4,5,6]]))

# 1  2  3  4
# 8  7  6  5
# 9  10 11 12
# 13 14 15 16

# 1,2,3,4,5,12,16,15,14,13,9,8,7,6,11,10

# 1 2 3
# 6 5 4
# 7 8 9
# 1,2,3,4,9,8,7,6,5