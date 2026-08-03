'''
def permutations(nums):
    result = []
    current = []
    used = set()              # tracks which numbers are used

    def backtrack():
        # base case — used all numbers
        if len(current) == len(nums):
            result.append(current[:])
            return

        # try every number
        for num in nums:
            if num in used:       # skip already used numbers
                continue

            # make choice
            current.append(num)
            used.add(num)

            # explore
            backtrack()

            # undo
            current.pop()
            used.remove(num)

    backtrack()
    return result

print(permutations([1, 2, 3]))
'''

def get_permutations(nums):
    current = []
    results = []
    used = set()
    def backtrack():

        # base case
        if len(nums) == len(current):
            results.append(current[:])
            return 

        # smaller problem passed down:
        # we are looping on this: for num in nums:
        # it will start with first element....
        # with recursion it will find all the combinations 
        # and then it will go the next element of nums and do 
        # the same
        for n in nums:
            if n in used:
                continue
            #one call do before recursing:
            current.append(n) # make choice
            used.add(n)

            backtrack() # explore

            current.pop() # undo
            used.remove(n)

    backtrack()
    return results

print(get_permutations([1, 2, 1]))