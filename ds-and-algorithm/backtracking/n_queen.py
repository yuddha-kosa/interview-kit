def solve_n_queens(n):
    #chess = [[0]*n for _ in range(n)]
    path = []
    result = []

    def is_valid(row, col):

        for prev_row in range(row-1, -1, -1):
            prev_col = path[prev_row]
            if col == prev_col:
                return False
            if abs(row-prev_row) == abs(col-prev_col):
                return False
        return True

    def backtrack(i):
        if len(path) == n:
            result.append(path[:])
            return
        
        for k in range(n):
            if is_valid(i, k):
                path.append(k)
                backtrack(i+1)
                # if the row at i+1 did not find any position then the row that had called it will
                # move the queen to the next column by first popping and then chosing the next option in the
                # column and then again it will call next row and try to find the right position.
                path.pop() 

    
    backtrack(0)
    return result

print(solve_n_queens(4))

'''
time: O(n × n!)
space: O(n)

recursion depth:  O(n)  — confirmed: depth=4 for n=4, depth=8
                            for n=8, exactly matching
path array:       O(n)  — confirmed: never exceeds n entries

Total auxiliary space = O(n) + O(n) = O(2n) = O(n)
                                       (Big-O drops the constant)
'''