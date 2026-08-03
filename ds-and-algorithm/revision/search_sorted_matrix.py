def search_sorted(matrix, target):

    left = 0
    right = (len(matrix)*len(matrix[0]))-1

    while left <= right:
        mid = (left+right) // 2
        row = mid//len(matrix[0])
        col = mid%len(matrix[0])
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            right = mid - 1
        else:
            left = mid + 1
    return False 


print(search_sorted([[1,2,3],[4,5,6],[7,8,9]], 6))