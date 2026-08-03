def max_area_container(arr):
    left = 0
    right = len(arr)-1
    max_area = 0
    while left < right:
        length = min(arr[left], arr[right])
        width = right-left
        area = length*width
        max_area = max(max_area, area)

        if arr[left] < arr[right]:
            left += 1
        else:
            right -= 1

    return max_area

       


    
print(max_area_container([2,3,10,5,7,8,9]))
print(max_area_container([1,1,1,1]))