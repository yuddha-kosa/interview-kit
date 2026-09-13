def min_sub_array_len(target: int, nums: list[int]) -> int:
    # Initialize the minimum length with infinity
    min_length = float('inf')
    
    current_sum = 0
    left = 0
    
    # Expand the window using the right pointer
    for right in range(len(nums)):
        current_sum += nums[right]
        
        # While the current window sum satisfies the condition
        while current_sum >= target:
            # Update the minimum length found so far
            min_length = min(min_length, right - left + 1)
            
            # Shrink the window from the left to find a smaller valid subarray
            current_sum -= nums[left]
            left += 1
            
    # If min_length wasn't updated, it means no valid subarray exists
    return min_length if min_length != float('inf') else 0

# Example Usage:
target_val = 7
nums_arr = [2, 3, 1, 2, 4, 3]
print(min_sub_array_len(target_val, nums_arr))
# Output: 2 (The shortest subarray is)
