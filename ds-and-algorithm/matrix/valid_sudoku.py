def valid_sudoku(board):

    for i in range(9):
        seen = set()
        for j in range(9):
            if board[i][j].isdigit(): 
                if board[i][j] in seen:
                    return False
                seen.add(board[i][j])
    
    for j in range(9):
        seen = set()
        for i in range(9):
            if board[i][j].isdigit(): 
                if board[i][j] in seen:
                    return False
                seen.add(board[i][j])
    

    for square in range(9):
        seen = set()
        for i in range(3):
            for j in range(3):
                row = (square//3)*3+i
                col = (square%3)*3+j

                if board[row][col].isdigit(): 
                    if board[row][col] in seen:
                        return False
                    seen.add(board[row][col])
    return True

def valid_sudoku1(board):
    rows  = [set() for _ in range(9)]
    cols  = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]

    for i in range(9):
        for j in range(9):
            val = board[i][j]
            if val == '.':
                continue

            box_id = (i//3)*3 + (j//3)

            if val in rows[i] or val in cols[j] or val in boxes[box_id]:
                return False

            rows[i].add(val)
            cols[j].add(val)
            boxes[box_id].add(val)

    return True

'''
rows = [set() for _ in range(9)]

rows[0] = set()    ← set for row 0
rows[1] = set()    ← set for row 1
rows[2] = set()    ← set for row 2
...
rows[8] = set()    ← set for row 8
'''