def minumum_in_rotated_arr(arr):
    left = 0
    right = len(arr)-1
    smallest = 0
    while left <= right:
        mid = (left+right)//2

        if arr[mid] < arr[right]:
            right = mid
        else:
            left = mid+1
        smallest = arr[mid]
    return smallest

print(minumum_in_rotated_arr([8,9,10,11,1,2,3,4,6,7]))

print(minumum_in_rotated_arr([1, 2,3,4, 8,9,10,11]))
print(minumum_in_rotated_arr([1, 2,3,4, 5]))
print(minumum_in_rotated_arr([3,4,5,1,2]))