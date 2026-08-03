def peak_element(arr):
    left = 0
    right = len(arr)-1

    while left <= right:
        mid = (left+right)//2

        left_val  = arr[mid-1] if mid > 0 else float('-inf')
        right_val = arr[mid+1] if mid < len(arr)-1 else float('-inf')

        #if arr[mid-1] < arr[mid] > arr[mid+1]:
        if left_val < arr[mid] > right_val:
            return mid
        #elif arr[mid] > arr[mid+1]:
        elif arr[mid] > right_val:
            right = mid-1
        else:
            left = mid+1
    return -1

print(peak_element([1,5,2,4,1]))
print(peak_element([3,4,3,2,1]))