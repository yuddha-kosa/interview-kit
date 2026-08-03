def saddle_number(matrix):

    saddle = []

    # find smallest in each row
    # keep position and value in a hashmap
    # use row,col as key and value as value of hash.
    smallest_pair = {}
    for i in range(len(matrix)):
        smallest = matrix[i][0]
        index = [i,0]
        for j in range(1, len(matrix[0])):
            if matrix[i][j] < smallest:
                smallest = matrix[i][j]
                index = [i,j]
        smallest_pair[tuple(index)] = smallest    
    
    for index, smallest_row in smallest_pair.items():
        row,col = index
        largest = smallest_row
        sad = True
        for i in range(len(matrix)):
            if largest < matrix[i][col]:
                sad = False
                break
        if sad:
            saddle.append(largest) 
    return saddle
print(saddle_number([[5,2,9], [4,1,6], [7,3,8]]))
print(saddle_number([[20,30,40], [10,25,35], [5,15,45]]))

        

