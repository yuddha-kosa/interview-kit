def binary_search(arr, target):

    left = 0
    right = len(arr)-1

    while left <= right:
        mid = (left+right)//2
        if arr[mid] == target:
            print(f"left: {left}, right: {right}, mid: {mid}, found: {arr[mid]}")
            return arr[mid]
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1 # not found

print(binary_search([2,4,6,8,12], 2))
print(binary_search([2,4,6,8,12], 7))

