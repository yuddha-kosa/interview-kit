def max_sub_array(arr):
    max_sum = arr[0]

    current = arr[0]
    for i in range(1, len(arr)):
        current = current + arr[i] 
        if current <= arr[i]:
            current = arr[i]

        max_sum = max(max_sum, current) 
    return max_sum




print(max_sub_array([-1,2,3,-5,4]))

print(max_sub_array([0]))
print(max_sub_array([10,-2,3,1]))
print(max_sub_array([-6,3,-1,-2]))