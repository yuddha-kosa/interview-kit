def sort_insertion(arr):

    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        # shift
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr



print(sort_insertion([5, 3, 8, 1, 2]))
print(sort_insertion([0,3,1,5,2,7,8,4]))
print(sort_insertion([10,30,1,5,20,70,8,4]))
print(sort_insertion([1,2,3,4,5]))