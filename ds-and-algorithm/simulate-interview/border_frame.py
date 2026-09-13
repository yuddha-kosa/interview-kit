def border_frame(matrix, thickness):

    left = 0
    right = len(matrix[0])-1
    top = 0
    bottom = len(matrix)-1
    thickness_limit = 0
    exp_element = matrix[0][0]

    if len(matrix) <= 2 * thickness or len(matrix[0]) <= 2 * thickness:
        return False
    
    while left <= right and top <= bottom:
        if thickness_limit == thickness:
            return True
        for i in range(left, right+1):
            if matrix[top][i] != exp_element:
                return False
        top += 1

        for j in range(top, bottom+1):
            if matrix[j][right] != exp_element:
                return False
        right -= 1

        if left <= right:
            for k in range(right, left-1, -1):
                if matrix[bottom][k] != exp_element:
                    return False
        bottom -= 1
        if top <= bottom:
            for l in range(bottom, top-1, -1):
                if matrix[l][left] != exp_element:
                    return False
        left += 1


        thickness_limit += 1 
    return True


matrix = [['#', '#', '#', '#'],
 ['#', 'A', 'B', '#'],
 ['#', '#', '#', '#']]
thickness = 2
print(border_frame(matrix, thickness))


def border_frame1(matrix, thickness):
    rows = len(matrix)
    cols = len(matrix[0]) if rows > 0 else 0
    
    # Validation: Ensure matrix is large enough to have an inner core left over
    if rows <= 2 * thickness or cols <= 2 * thickness:
        return False
        
    # Pick the target character from the top-left corner
    target = matrix[0][0]
    
    for r in range(rows):
        for c in range(cols):
            # Check if the current coordinate sits within the border zone
            is_border = (r < thickness or 
                         r >= rows - thickness or 
                         c < thickness or 
                         c >= cols - thickness)
                         
            if is_border:
                if matrix[r][c] != target:
                    return False
                    
    return True

matrix = [['#', '#', '#', '#'],
          ['#', 'A', 'B', '#'],
          ['#', '#', '#', '#']]

print(border_frame(matrix, 1))  # Output: True
print(border_frame(matrix, 2))  # Output: False (Correctly catches the lack of an inner core)
