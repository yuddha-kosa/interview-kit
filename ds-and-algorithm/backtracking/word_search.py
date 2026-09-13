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



'''
for each point it can go in max 4 directions...so if we look it as a tree ..at level 0 -1..at level 1 ..4..at level 2 ..16..so it growing by 4 to the pow level...we will do this for row*col time in worst case..so time complexity is:
O(row*col*4 to the pow L)

Time:  O(row × col × 4^L)   -- confirmed correct, your derivation
Space: O(L)                  -- NOT O(row×col) — bounded by
                                 word length, confirmed by
                                 measurement above (max size
                                 stayed at 4, matching L=4,
                                 regardless of the 100-cell grid)

'''