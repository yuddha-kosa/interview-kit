def bubble_sort(arr):

    for i in range(len(arr)-1):
        swapped = False
        for j in range(len(arr)-i-1):
            if arr[j+1] < arr[j]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if not swapped: # j is iteration for every i from 0, if swapping did not take place that means array is already sorted 
            break
    return arr


print(bubble_sort([5, 3, 8, 1, 2]))
print(bubble_sort([0,3,1,5,2,7,8,4]))
print(bubble_sort([10,30,1,5,20,70,8,4]))
print(bubble_sort([1,2,3,4,5]))