def maximum_subarray(arr):
    max_sum = arr[0]
    #coordinates = [] 

    for i in range(len(arr)):
        sum = arr[i]
        max_sum = max(sum, max_sum) 
        for j in range(i+1, len(arr), 1):
            sum = sum + arr[j]
            #if sum > max_sum:
                #coordinates = [i,j]
                #print(f"max_sum: {sum} coordinates: {coordinates}, subarr: {arr[i:j+1]}")
            max_sum = max(sum, max_sum)
    return max_sum

print(maximum_subarray([-1,2,3,-5,45]))
print(maximum_subarray([10,-2,3,1]))
            
print("***********Kadane**********")
# if current sume is negative adding it to the next element will make it even smaller.
# if all the elements of a sub-arr is smaller than 0 then the max sum will always be -1.
# 
def maximum_subarray_kadane(arr):
    max_sum = arr[0]
    current_sum = 0 
    right = 0

    while right < len(arr):
        if current_sum > 0:
            current_sum += arr[right]
        else:
            current_sum = arr[right]
        max_sum = max(current_sum, max_sum)
        right += 1
    return max_sum

        

print(maximum_subarray_kadane([-1,2,3,-5,45]))
print(maximum_subarray_kadane([10,-2,3,1]))
            

print("*********************")

def maximum_subarray_kadane1(arr):
    max_sum = arr[0]
    current_sum = arr[0]
    for i in range(1, len(arr)):
        current_sum = max(arr[i], current_sum+arr[i])
        max_sum = max(current_sum, max_sum)
    return max_sum

        

print(maximum_subarray_kadane1([-1,2,3,-5,45]))
print(maximum_subarray_kadane1([10,-2,3,1]))
            