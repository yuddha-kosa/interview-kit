def crop_bounding_box(matrix):
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    
    min_row, max_row = rows, -1
    min_col, max_col = cols, -1
    
    # Step 1: Scan the grid to find the boundary limits
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 1:  # Assuming 1 is our target pixel
                if r < min_row: min_row = r
                if r > max_row: max_row = r
                if c < min_col: min_col = c
                if c > max_col: max_col = c
                
    # Step 2: Handle edge case where no targets were found
    if max_row == -1:
        return []
        
    # Step 3: Slice and return the cropped sub-matrix
    cropped_matrix = []
    for r in range(min_row, max_row + 1):
        cropped_matrix.append(matrix[r][min_col:max_col + 1])
        
    return cropped_matrix
