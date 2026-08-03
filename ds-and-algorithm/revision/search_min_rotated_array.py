def min_rotated_array(arr):
    left = 0
    right = len(arr)-1

    while left < right:
        mid = (left+right)//2

        if arr[mid] > arr[right]:
            left = mid + 1
        else:
            right = mid
    return arr[right]

print(min_rotated_array([8,9,10,1,2,3,4]))
print(min_rotated_array([10,12,14,3,6,8]))
