Let's cover the three you named, plus the other commonly-tested ones worth having ready.

---

# Array Patterns — Quick Reference

---

## 1. Sliding Window

```
Maintain a WINDOW (contiguous range) that EXPANDS (right
pointer moves forward) and SHRINKS (left pointer moves
forward) based on a CONSTRAINT.

Use when: "contiguous subarray/substring" + some condition
          (sum, length, distinct count, etc.)
```

```python
def max_sum_subarray_size_k(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i-k]   # add new, remove old
        max_sum = max(max_sum, window_sum)
    return max_sum
```

---

## 2. Two Pointers

```
Two pointers moving TOWARD each other (usually from opposite
ends) or in a coordinated way, typically on a SORTED array.

Use when: "pair/triplet that sums to X", "reverse in place",
          "is palindrome"
```

```python
def two_sum_sorted(arr, target):
    left, right = 0, len(arr)-1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1
        else:
            right -= 1
    return []
```

---

## 3. Fast & Slow Pointers (Floyd's Cycle Detection)

```
Two pointers moving at DIFFERENT SPEEDS (slow moves 1 step,
fast moves 2 steps). If there's a CYCLE, they're GUARANTEED
to eventually meet.

Use when: "detect cycle", "find middle of linked list",
          "find duplicate number" (cycle-in-disguise problems)
```

```python
def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

---

## Other important patterns worth having ready

---

## 4. Prefix Sum

```
Precompute CUMULATIVE sums, so any RANGE SUM can be answered
in O(1), instead of re-summing every time.

Use when: "sum of range [i,j]" asked REPEATEDLY, or "subarray
          sum equals K"
```Confirmed correct (`9`).

Example 1 — Repeated range-sum queries

You'll be asked "what's the sum from index i to j" MANY times,
on the SAME array. Precompute once, answer every query in O(1).
class NumArray:
    def __init__(self, nums):
        self.prefix = [0]*(len(nums)+1)
        for i in range(len(nums)):
            self.prefix[i+1] = self.prefix[i] + nums[i]

    def sumRange(self, i, j):
        return self.prefix[j+1] - self.prefix[i]

nums = [1,3,5,7,9,11]
na = NumArray(nums)
print('array:', nums)
print('sumRange(1,3):', na.sumRange(1,3))
print('sumRange(0,5):', na.sumRange(0,5))
print('sumRange(2,2):', na.sumRange(2,2))

Example 2 — Subarray Sum Equals K (the more interesting application)
Count how many CONTIGUOUS subarrays sum to EXACTLY K.

Key insight: if prefix[j] - prefix[i] = K, then the subarray
from i+1 to j sums to K. So for each position j, we ask:
"has some EARLIER prefix sum equal to (prefix[j] - K)?" — and
a HASH MAP lets us answer this instantly.

```python
def subarray_sum_equals_k(nums, k):
    count = 0
    prefix_sum = 0
    seen = {0: 1}
    for num in nums:
        prefix_sum += num
        needed = prefix_sum - k
        if needed in seen:
            count += seen[needed]
        seen[prefix_sum] = seen.get(prefix_sum, 0) + 1
    return count

nums = [1,2,3,-3,4]
k = 3
print(subarray_sum_equals_k(nums, k))

---

## 5. Merge Intervals

```
Given overlapping intervals, SORT by start time, then merge
any that overlap.

Use when: "merge intervals", "meeting rooms", "insert interval"



```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    result = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= result[-1][1]:      # overlaps with previous
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
```

---

## 6. Cyclic Sort

```
Specifically for arrays containing numbers in a KNOWN range
(like 1 to n), place EACH number at its "correct" index
directly, in ONE pass.

Use when: "find missing number", "find duplicate", array
          contains 1 to n (or 0 to n-1)
```

```python
def cyclic_sort(nums):
    i = 0
    while i < len(nums):
        correct_index = nums[i] - 1
        if nums[i] != nums[correct_index]:
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1
    return nums
```

---

# Summary table

```
Pattern           When to reach for it                         Time
Sliding Window    contiguous subarray + size/sum constraint     O(n)
Two Pointers      sorted array, pair/triplet sum, palindrome    O(n)
Fast/Slow         cycle detection, middle element                O(n)
Prefix Sum        REPEATED range-sum queries                     O(n) build, O(1) query
Merge Intervals   overlapping ranges                              O(n log n)
Cyclic Sort       array with values in range [1,n] or [0,n-1]    O(n)
```

Given the timeline, want to pick 1-2 of these to actually CODE from scratch and verify, or move to the next revision topic (Data Structure operations)?