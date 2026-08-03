def quick_sort(arr, low, high):

    if low < high:
        #print(arr[low:high+1])
        position = partition(arr, low, high)
        quick_sort(arr, low, position-1)
        quick_sort(arr, position+1, high)

def partition(arr, low, high):
    pivot = low
    left = low + 1
    right = high

    while left <= right:
        if arr[left] > arr[pivot] and arr[right] < arr[pivot]:
            arr[left], arr[right] = arr[right], arr[left]
            left += 1
            right -= 1
        elif arr[right] >= arr[pivot]:
            right -= 1
        elif arr[left] <= arr[pivot]:
            left += 1

    arr[pivot], arr[right] = arr[right], arr[pivot]
    print(f"left: {left}, right: {right}, arr: {arr}")
    return right

#arr = [5,3,8,1,2]
#arr = [3, 6, 8, 10, 1, 2, 1]
#arr = [5,1,2,3,4]
arr = [1,2,3,4,5]
quick_sort(arr, 0, len(arr)-1)
print(arr)


'''
Quick sort:
DO work first (partition) → recurse left → recurse right
Work happens on the way DOWN
No work on the way back up

1. Partition (work)
2. Recurse left
3. Recurse right
4. Nothing on return ← no merge step


Pre-order:   work → left → right    (quick sort)
In-order:    left → work → right    (BST traversal)
Post-order:  left → right → work    (merge sort)

Why it matters:
Merge sort:   can't sort until sub-problems solved
              needs results from below → post-order

Quick sort:   partitions BEFORE recursing
              sub-arrays already partially sorted
              no merge needed on return → pre-order

One sentence:
Quick sort is pre-order divide and conquer —
work (partition) happens before recursion,
nothing happens on the way back up.
'''