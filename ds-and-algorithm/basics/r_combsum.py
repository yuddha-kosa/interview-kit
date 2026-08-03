'''
Given a list of distinct numbers and a target:
find all combinations that sum to target.
Same number can be used multiple times.

nums = [2, 3, 6, 7], target = 7

Answer:
[2, 2, 3]
[7]
'''

def combination_sum(nums, target):
    results = []
    current = []

    def backtrack(index):

        # base condition.
        if sum(current) == target:
            results.append(current[:])
            return
        if sum(current) > target or index == len(nums):
            return
        
        # call before recursion

        # make choice
        current.append(nums[index])

        # explore
        backtrack(index)

        # undo
        current.pop()

        # smaller problem
        backtrack(index+1)

    backtrack(0)
    return results

print(combination_sum([2, 3, 6, 7], 7))