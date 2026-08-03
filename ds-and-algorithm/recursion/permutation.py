def permutation(nums):
    path = []
    results = []
    def backtrack(choices):

        if len(path) == len(nums):
            results.append(path[:])
            return

        for choice in choices:
            if choice not in path:
                path.append(choice)
                backtrack(choices)
                path.pop()

    backtrack(nums)
    return results



print(permutation([1,2,1]))
print(permutation([1,2,3]))