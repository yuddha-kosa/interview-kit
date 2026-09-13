def search_sorted(matrix,target):
    left = 0
    right = (len(matrix)*len(matrix[0]))-1
    rows = len(matrix)
    col = len(matrix[0])

    while left <= right:

        mid = (left+right)//2
        x = mid//col
        y = mid%col

        if matrix[x][y] == target:
            return True
        if matrix[x][y] > target:
            right = mid-1
        else:
            left = mid+1 
    return False

print(search_sorted([[1,2,3],[4,5,6],[7,8,9]], 7))