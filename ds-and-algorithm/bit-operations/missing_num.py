def missing_number(arr):
    '''
    if arr[0] != 0:
        return 0
    for i in range(len(arr)-1):
        if arr[i+1]-arr[i] > 1:
            return arr[i]+1
    '''
    result = len(arr)

    for i in range(result):
        # 0,1,2 ---> 0,1,3 --> 3
        result = i^result # start with i= 0 and result = 3, next time new i and result. 
        result = arr[i]^result
    return result

print(missing_number([0,1,3]))
print(missing_number([1,2]))

# 0^3^0^1^1^2^3
'''
0^3 = 3 = 11
3^0 = 3 = 11
3^1 = 2 = 10
2^1 = 3 = 11
3^2 = 01 = 1
1^3 = 10 = 2
'''