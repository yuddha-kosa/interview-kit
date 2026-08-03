def merge_sort(arr):
    #start = 0
    #end = len(arr)-1
    # base condition
    if len(arr) <= 1:
        return arr

    # recursion
    mid = len(arr) // 2
    #mid = (start + end)//2
    # problem becoming smaller
    left_arr = merge_sort(arr[:mid])
    right_arr = merge_sort(arr[mid:])
    return merge_arr(left_arr, right_arr)
    
def merge_arr(left_arr, right_arr):
    merge_list = []
    left = 0
    right = 0

    while left < len(left_arr) and right < len(right_arr):
        if left_arr[left] <= right_arr[right]:
            merge_list.append(left_arr[left])
            left += 1
        else:
            merge_list.append(right_arr[right])
            right += 1
        
    for i in range(left, len(left_arr)):
        merge_list.append(left_arr[i])

    for i in range(right, len(right_arr)):
        merge_list.append(right_arr[i])
            

    return merge_list

print(merge_sort([5, 3, 8, 1, 2]))

# time: O(nlog n)
# space: O(n)

'''
Post-order (like merge sort):
split → recurse left → recurse right → THEN do work (merge)
Work happens on the way UP

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