def insertion_sort(arr):
    result = [arr[0]]
    for i in range(1,len(arr)):
        result.append(arr[i])
        for j in range(len(result)-1, 0, -1):
            if result[j] < result[j-1]:
                result[j], result[j-1] = result[j-1], result[j]
    return result 

print(insertion_sort([5, 3, 8, 1, 2]))
print(insertion_sort([0,3,1,5,2,7,8,4]))
print(insertion_sort([10,30,1,5,20,70,8,4]))
print(insertion_sort([1,2,3,4,5]))

print("*******************************")
# treate the same array's one part as sorted and another part as unsorted
# take one element at a time and check if it's at the right position in the sorted part ?
# if not then move each element in the sorted part by one and create an empty place for the
# current key element and keep it there.
def insertion_sort1(arr):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1

        # if the previous element is greater than the key, then shift it to the right
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

print(insertion_sort1([5, 3, 8, 1, 2]))
print(insertion_sort1([0, 3, 1, 5, 2, 7, 8, 4]))
print(insertion_sort1([10, 30, 1, 5, 20, 70, 8, 4]))
print(insertion_sort1([1, 2, 3, 4, 5]))

# time: O(n*n)
# space O(1)