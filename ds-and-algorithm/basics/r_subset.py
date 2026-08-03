def subset(nums):
    results = []
    current = []

    def backtrack(index):
        
        # base case
        if len(nums) == index:
            results.append(current[:])
            return
        
        # call before recursion
        # make choice
        current.append(nums[index])

        # explore
        backtrack(index+1)

        # undo
        current.pop()

        #smaller problem

        backtrack(index+1)
    backtrack(0)
    return results


print(subset([1,2,3]))

