def merge_sort(arr):
    
    if len(arr) <= 1:
        return arr 

    mid = (len(arr))//2

    left_sub_arr = merge_sort(arr[:mid])
    right_sub_arr = merge_sort(arr[mid:])
    return merge_arr(left_sub_arr, right_sub_arr)

def merge_arr(left, right):
    l = 0
    r = 0
    result = []

    while l < len(left) and r < len(right):
        if left[l] <= right[r]:
            result.append(left[l])
            l += 1
        else:
            result.append(right[r])
            r += 1
        
    while l < len(left):
            result.append(left[l])
            l += 1
    while r < len(right):
            result.append(right[r])
            r += 1
    return result

print(merge_sort([5, 3, 8, 1, 2]))



    
