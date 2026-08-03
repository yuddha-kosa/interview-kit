def selection_sort(arr):

    for left in range(len(arr)-1):
        min_index = left
        # find shotest in the right side
        for uns in range(left+1, len(arr)):
            if arr[uns] < arr[min_index]:
                min_index = uns
        # swap
        arr[left], arr[min_index] = arr[min_index], arr[left]
    return arr
        

            



print(selection_sort([3,4,8,1,5,7,9,11]))
print(selection_sort([5,4,3,2,1]))