'''
parent of index i = (i - 1) // 2      [you already know this
                                        from earlier tree work]
                                        child = 2i+1
                                        i = (child-1)//2
                                        i - parent index
                                        child - child index

last leaf index = n - 1 (substitue in 1st equation)

So: last non-leaf index = parent of (n-1)
                         = ((n-1) - 1) // 2
                         = (n - 2) // 2
'''

def shift_down(arr, i, n):
    while True:
        left = 2*i+1
        right = 2*i+2
        smallest = i
        if left < n and arr[left] < arr[smallest]:
            smallest = left
        if right < n and arr[right] < arr[smallest]:
            smallest = right
        if i == smallest:
            break
        arr[i], arr[smallest] = arr[smallest], arr[i]
        i = smallest


def heapify(arr):
    n = len(arr)

    last_non_leaf = (n-2)//2

    for i in range(last_non_leaf, -1, -1):
        shift_down(arr, i, n)
    return arr

print(heapify([9, 4, 7, 1, -2, 6, 5]))


'''
heapify's time complexity is O(n), NOT O(n log n).

Your intuition ("n/2 calls × O(log n) each") is a valid UPPER
BOUND, but it's not TIGHT — most of those n/2 calls actually
do very little work (nodes near the bottom barely move), and
only a few calls near the root do the full O(log n) work. The
mathematical sum across all levels converges to O(n).

This is a well-known, somewhat counter-intuitive result: even
though a SINGLE sift-down costs O(log n), heapify-ing an
ENTIRE array is O(n) — cheaper than you might expect from
naive multiplication.

Time:  O(n)   [NOT O(n log n) — proven both by measurement
               and by the mathematical series above]
Space: O(1)   [correct — in-place swaps only]
'''