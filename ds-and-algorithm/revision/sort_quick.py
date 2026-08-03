def quick_sort(arr, low, high):

    if low < high:
        pivot = partition(arr, low, high)
        quick_sort(arr, low, pivot-1)
        quick_sort(arr, pivot+1, high)

def partition(arr, low, high):
    pivot = low
    left = low + 1
    right = high

    while left <= right:
        if arr[left] > arr[pivot] and arr[right] < arr[pivot]:
            # swap
            arr[left], arr[right] = arr[right], arr[left]
            left += 1
            right -= 1
        elif arr[left] <= arr[pivot]:
            left += 1
        elif arr[right] >= arr[pivot]:
            right -= 1
    # final position left will cross pivot on the greater side and right will cover pivot on the
    # smaller side, swap pivot with right because the pivot we choose is on the start of the arr
    # on the left side...so if we swap pivot with the right eveything left will remain small and right will
    # remain big.
    arr[right], arr[pivot] = arr[pivot], arr[right]
    return right
        




arr = [1,2,3,4,5]
quick_sort(arr, 0, len(arr)-1)
print(arr)