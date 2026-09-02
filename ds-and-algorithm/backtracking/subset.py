def subset(nums):
    length = len(nums)
    path = []
    results = []

    def backtrack(i):
        if i == length:
            results.append(path[:])
            return
        
        # we have two options here eiter to select a number or not select.
        # once we make our choice we will explore that path.

        # choice 1: select the number and explore.
        path.append(nums[i])
        backtrack(i+1)

        # choice 2: not select the number and explore.
        path.pop()
        backtrack(i+1)


    backtrack(0)
    return results


print(subset([2,4,6]))

'''
Time:
    O(n · 2^n)

Space:
    O(n) auxiliary
    O(n · 2^n) including output
'''