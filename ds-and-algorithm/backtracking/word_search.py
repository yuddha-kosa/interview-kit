def word_search(board, word):
    path = []
    visited = set()
    rows = len(board)
    cols = len(board[0])

    def backtrack(i, j, k):
        if "".join(path) == word:
            print("path:", path)
            return True
        #if k == len(word):
        #    return True
        
        if i < 0  or i >= rows or j < 0 or j >= cols or board[i][j] != word[k] or (i,j) in visited:
            return False
        
        path.append(word[k])
        visited.add((i,j))
        if backtrack(i, j-1, k+1):
            return True
        if backtrack(i, j+1, k+1):
            return True
        if backtrack(i-1, j, k+1):
            return True
        if backtrack(i+1, j, k+1):
            return True
        path.pop()
        visited.remove((i,j))

        return False
            


    for row in range(rows):
        for col in range(cols):

            if backtrack(row, col, 0):
                return True

    return False



word = "ABCCED"
print(word_search([['A','B','C','E'], ['S','F','C','S'], ['A','D','E','E']], word))

word1 = "ABCD"
print(word_search([['A','B'], ['C','D']], word1))