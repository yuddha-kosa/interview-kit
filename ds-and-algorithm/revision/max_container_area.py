
def max_cont_area(arr):

    max_area = 0
    left = 0
    right = len(arr)-1

    while left < right:
        width = right-left

        height = 0
        if arr[left] < arr[right]:
            height = arr[left]
            left += 1
        else:
            height = arr[right]
            right -= 1

        max_area = max(max_area, (width*height))
    
    return max_area
    


print(max_cont_area([2,3,10,5,7,8,9]))