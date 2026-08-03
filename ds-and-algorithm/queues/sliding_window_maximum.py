def sliding_window_maximum(nums, k):
    left = 0
    right = k

    result = []
    while right <= len(nums):
        max_num = max(nums[left:right])
        result.append(max_num)
        left += 1
        right += 1
    return result

print(sliding_window_maximum([1,3,-1,-3,5,3,6,7], 3))

print("*******************")

from collections import deque
def sliding_window_maximum1(nums, k):
    dq_nums = deque()
    result = []

    for i in range(len(nums)):
        # pop ifrom right until the largest is left in the queue.
        while dq_nums and nums[dq_nums[-1]] < nums[i]:
            dq_nums.pop()
        # add element
        dq_nums.append(i)
        # pop from left if element at 0th position is smaller than the window size.
        if dq_nums[0] < i-k+1:
            dq_nums.popleft()

        if i >= k-1:
            result.append(nums[dq_nums[0]])
            print(f"largest in range: {i} to {i-k+1} is: {dq_nums[0]}")
    return result

print(sliding_window_maximum1([1,3,-1,-3,5,3,6,7], 3))