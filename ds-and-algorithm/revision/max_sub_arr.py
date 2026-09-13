def maximum_subarray(arr):

    maximum = arr[0] 
    curr = arr[0] 
    index = 0
    prev_index = 0
    max_index = (0,0)
    for i in range(1,len(arr)):
        if arr[i] > curr+arr[i]:
            curr = arr[i]
            index = i
            prev_index = i
        else:
            curr = arr[i] + curr
            index = i
        if curr > maximum:
            max_index = (prev_index, index)
        maximum = max(maximum, curr)
    print("index: ", max_index)
    return maximum




print(maximum_subarray([-1,2,3,-5,4]))
print(maximum_subarray([-10,-2,-3,-5,-4]))

'''
time: O(n)
space: O(1)
'''