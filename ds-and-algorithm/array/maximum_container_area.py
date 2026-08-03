def max_container(arr):
    area = 0
    coordinate = []
    for i in range(len(arr)-1):
        for j in range(i+1, len(arr)):
            min_of = min(arr[i], arr[j])
            area_cal = min_of * (j-i)
            if area_cal > area:
                area = area_cal
                coordinate = [i, j]
    print(f"coordinate: {coordinate}")
    return area

print(max_container([2,3,10,5,7,8,9]))
print(max_container([1,1,1,1]))

print("*************Two pointer**************")
# by moving the pointers in opposite direction we are trying to find the maximun height and maximum
# depth with the highest area.
def max_container1(arr):
    left = 0
    right = len(arr)-1
    area = 0
    while (left < right):
        height = min(arr[left], arr[right])
        width = right-left
        current_area = height * width
        area = max(current_area, area)
        if arr[left] < arr[right]:
            left += 1
        else:
            right -= 1
    return area


print(max_container1([2,3,10,5,7,8,9]))
print(max_container1([1,1,1,1]))