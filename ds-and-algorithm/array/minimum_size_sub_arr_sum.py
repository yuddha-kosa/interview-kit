
# Given an array of positive integers nums and a positive integer target,
# return the minimal length of a subarray whose sum is greater than or equal to target.
# If there is no such subarray, return 0 instead.
def minSubArrayLen(nums, target):
    min_sub_arr = float('inf')
    left = 0
    curr_sum = 0

    for right in range(len(nums)):
        curr_sum += nums[right]
        if curr_sum >= target:
            min_sub_arr = min(min_sub_arr, (right-left+1))

            
            while left < right:
                curr_sum = curr_sum-nums[left]
                left += 1
                if curr_sum >= target:
                    min_sub_arr = min(min_sub_arr, (right-left+1))
    if min_sub_arr == float('inf'):
        return 0
    else: 
        return min_sub_arr


print(minSubArrayLen([2,3,1,2,4,3], 7))