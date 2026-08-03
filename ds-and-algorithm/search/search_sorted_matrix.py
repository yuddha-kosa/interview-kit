def search_sorted(matrix,target):

    for i in range(len(matrix)):
        #print(f"i: {i}, len: {len(matrix)}")
        for j in range(len(matrix[i])):
            #print(f"j: {j}, len: {len(matrix[i])}")
            if matrix[i][j] == target:
                return True
    return False

print(search_sorted([[1,2,3],[4,5,6],[7,8,9]], 6))



def search_sorted1(matrix,target):

    oleft = 0
    oright = len(matrix)-1

    while oleft <= oright:
        omid = (oleft+oright)//2

        if matrix[omid][0] <= target <= matrix[omid][len(matrix[omid])-1]:
            ileft = 0
            iright = len(matrix[omid])-1

            while ileft <= iright:
                imid = (ileft+iright)//2
                if target == matrix[omid][imid]:
                    return True
                elif target <  matrix[omid][imid]:
                    iright = imid-1
                else:
                    ileft = imid+1 
        elif target < matrix[omid][0]:
            oright = omid-1
        else:
            oleft = omid+1 
    return False



print(search_sorted1([[1,2,3],[4,5,6],[7,8,9]], 7))