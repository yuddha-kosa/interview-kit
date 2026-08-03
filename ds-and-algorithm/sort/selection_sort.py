# select the smallest and swap it with the first element in the unsorted array.
# treat whole array initially as unsorted part and then keep reducing it's width in every go.
def selection_sort(arr):

    unsorted = 0

    for i in range(len(arr)-1):
        smallest_index = i
        # find the minimum value in the unsorted part.
        for j in range(i+1, len(arr)):
            if arr[j] < arr[smallest_index]:
                # store the index of the smallest element.
                smallest_index = j
        # swap the smallest element with the first element in the unsorted array.
        arr[smallest_index], arr[unsorted] = arr[unsorted], arr[smallest_index]
        # increase the unsorted array by 1, meaning reduce the width of unsorted array. 
        unsorted += 1    
    return arr

# Insertion sort:  take next element, find its position in sorted portion
# Selection sort:  find minimum in unsorted portion, place at front

# Insertion: O(n) best case — already sorted
# Selection: O(n²) always   — always scans full unsorted portion


print(selection_sort([5, 3, 8, 1, 2]))