def longest_subarray_k_distinct(arr, k):

    distinct = {}
    max_arr = 0
    left = 0

    for right in range(len(arr)):
        distinct[arr[right]] = distinct.get(arr[right], 0) + 1
        while len(distinct) > k:
            distinct[arr[left]] -= 1
            if distinct[arr[left]] == 0:
                del(distinct[arr[left]])
            left += 1
        max_arr = max(max_arr, (right-left+1))
    
    return max_arr





nums = [1, 2, 1, 2, 3, ]
K = 2
print(longest_subarray_k_distinct(nums, K))