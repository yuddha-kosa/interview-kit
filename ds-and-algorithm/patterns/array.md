Here is a structured comprehensive review of the algorithmic patterns you covered, complete with all the corrected and optimized code examples for your notes.
------------------------------
## 1. Merge Intervals Pattern
Used when dealing with overlapping intervals. The core strategy is to sort the intervals by their start times so that overlapping intervals become adjacent, allowing a single linear pass to merge them.

* Time Complexity: $O(n \log n)$ due to sorting.
* Space Complexity: $O(n)$ to store the merged result.

def merge_intervals(intervals):
    if not intervals:
        return []
    
    # 1. Sort intervals by their starting values
    intervals.sort(key=lambda x: x[0])
    
    # Initialize the merged list with the first interval
    merged = [intervals[0]]
    
    # 2. Iterate through the rest of the intervals
    for current in intervals[1:]:
        last_merged = merged[-1]
        
        # If current interval overlaps with the last merged interval
        if current[0] <= last_merged[1]:
            # Merge them by updating the end of the last merged interval
            last_merged[1] = max(last_merged[1], current[1])
        else:
            # No overlap, safely append the current interval
            merged.append(current)
            
    return merged
# Example:# Input: [[1,3], [2,6], [8,10], [15,18]]# Output: [[1,6], [8,10], [15,18]]

------------------------------
## 2. Sliding Window (Dynamic Size)
Used for subarray or substring tracking. The window expands using a right pointer, while a left pointer dynamically adjusts to maintain or optimize constraints.
## A. Longest Subarray with at Most K Distinct Values
The window expands continuously. We track item frequencies in a hash map. The window only shrinks when the map size strictly exceeds $K$ (meaning duplicates do not trigger a shrink).

* Time Complexity: $O(N)$
* Space Complexity: $O(K)$

def longest_subarray_k_distinct(arr, k):
    if k == 0 or not arr:
        return 0
        
    frequency_map = {}
    max_length = 0
    left = 0
    
    for right in range(len(arr)):
        frequency_map[arr[right]] = frequency_map.get(arr[right], 0) + 1
        
        # Shrink only if unique keys exceed K
        while len(frequency_map) > k:
            left_element = arr[left]
            frequency_map[left_element] -= 1
            if frequency_map[left_element] == 0:
                del frequency_map[left_element]
            left += 1
            
        max_length = max(max_length, right - left + 1)
        
    return max_length
# Example: nums =, K = 2 -> Output: 4 ([1, 2, 1, 2])

## B. Longest Substring Without Repeating Characters (Optimized Jump)
Instead of shrinking step-by-step, a hash map tracks the last seen index of each character. When a repeat is found inside the current window boundaries, the left pointer instantly jumps past the original character's index.

* Time Complexity: $O(N)$
* Space Complexity: $O(\min(M, N))$ where $M$ is the character alphabet size.

def longest_substring_no_repeats(s: str) -> int:
    char_last_index = {}
    max_length = 0
    left = 0
    
    for right, char in enumerate(s):
        # Jump left pointer if duplicate is inside the current window
        if char in char_last_index and char_last_index[char] >= left:
            left = char_last_index[char] + 1
            
        char_last_index[char] = right
        max_length = max(max_length, right - left + 1)
        
    return max_length
# Example: "abcabcbb" -> Output: 3 ("abc")

## C. Minimum Size Subarray with Sum $\ge$ Target
Unlike looking for the longest window where we shrink to fix violations, here we shrink deliberately to minimize the window size as long as the current sum remains valid ($\ge \text{target}$).

* Time Complexity: $O(N)$
* Space Complexity: $O(1)$

def min_sub_array_len(target: int, nums: list[int]) -> int:
    min_length = float('inf')
    current_sum = 0
    left = 0
    
    for right in range(len(nums)):
        current_sum += nums[right]
        
        # Optimize by shrinking left as long as the sum is valid
        while current_sum >= target:
            min_length = min(min_length, right - left + 1)
            current_sum -= nums[left]
            left += 1
            
    return min_length if min_length != float('inf') else 0
# Example: target = 7, nums = [2, 3, 1, 2, 4, 3] -> Output: 2 ([4, 3])

------------------------------
## 3. Cyclic Sort Pattern
Ideal for arrays containing values within a defined range (e.g., $1$ to $n$ or $0$ to $n$). By treating values as indices, items are swapped directly into their "home slots" in a single pass without traditional nested iteration sorting.

* Time Complexity: $O(N)$ because every swap places at least one element into its permanent home slot.
* Space Complexity: $O(1)$ auxiliary space.

## A. Find the Missing Number (Range: $0$ to $n$)

def find_missing_number(nums):
    i, n = 0, len(nums)
    
    while i < n:
        correct_index = nums[i]
        if correct_index < n and nums[i] != nums[correct_index]:
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1
            
    for index in range(n):
        if nums[index] != index:
            return index
    return n
# Example: [3, 0, 1] -> Output: 2

## B. Find the Duplicate Number (Range: $1$ to $n$) — Loop Safe Version
To avoid infinite loops caused by duplicates fighting for the same index, we explicitly check if a number matches the value already resting at its correct_index before attempting a swap.

def find_duplicate_number(nums):
    i = 0
    while i < len(nums):
        correct_index = nums[i] - 1
        
        if i != correct_index:
            # If the home slot already contains this number, it's a duplicate!
            if nums[i] == nums[correct_index]:
                return nums[i]
            
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1
            
    return -1
# Example: [1, 3, 4, 2, 2] -> Output: 2

Would you like to save these notes to a specific file format like Markdown (.md) or PDF (.pdf), or should we move on to another algorithmic pattern like Two Pointers or Fast & Slow Pointers?

