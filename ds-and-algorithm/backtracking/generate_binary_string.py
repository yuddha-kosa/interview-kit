def generate_binary_string(n):

    result = []
    path = []

    def backtracking():

        if len(path) == n:
            result.append("".join(path))
            return
        
        for i in range(2):
            path.append(str(i))
            backtracking()
            path.pop()

    backtracking()
    return result

print(generate_binary_string(3))

'''
Time:  O(2^n) — n positions, 2 choices each, giving 2^n total
       strings (matches the Subsets pattern exactly)
Space: O(n) — recursion depth, plus O(2^n) if counting the
       output itself
'''