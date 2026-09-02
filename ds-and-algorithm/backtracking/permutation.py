def permutation(nums):
    length = len(nums)
    path = []
    result = []
    visited = set()

    def backtrack(i, visited):

        if len(path) == length:
            result.append(path[:])
            return
        
        for num in nums:
            #if num not in path:
            if num not in visited:
                path.append(num)
                visited.add(num)
                backtrack(i+1, visited)
                path.pop()
                visited.remove(num)

    backtrack(0, visited)
    return result

print(permutation([4,5,6]))

'''
time: O(n² · n!) #if num not in path:
time: O(n · n!) #if num not in visited:

space: O(n)
O(n · n!) including output
'''