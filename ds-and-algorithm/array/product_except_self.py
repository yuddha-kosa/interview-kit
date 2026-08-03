def product_except_self(arr):
    total_product = 1
    count = 0
    result = []
    total_non_zero_product = 1
    for i, n in enumerate(arr):
        if n != 0:
            total_product *= n
        elif n == 0:
            count += 1
    if count == 1:
        total_non_zero_product = total_product
        total_product = 0 
    if count > 1:
       total_non_zero_product = 0
       total_product = 0 

    for i, n in enumerate(arr):
        if n != 0:
            if total_product != 0:
                result.append(total_product//n)
            elif total_product == 0:
                result.append(0)
        elif n == 0:
            result.append(total_non_zero_product)
    return result

print(product_except_self([1,2,0,4,5]))
print(product_except_self([2,3,4,5]))

print(f"************prefix/suffix pattern******************")
def product_except_self1(arr):
    left =[1]* len(arr)
    right = [1]* len(arr)
    result = [] 
    for i in range(1, len(arr)):
        left[i] = left[i-1]*arr[i-1]
    for i in range(len(arr) - 2, -1, -1):
        right[i]= (right[i+1]*arr[i+1])
    for i in range(len(left)):
        result.append(left[i]*right[i])
    return result

print(product_except_self1([1,2,0,4,5]))
print(product_except_self1([2,3,4,5]))

print(f"*************Using two pointer approach and suffix frefix*****************")
def product_except_self2(arr):
    left =[1]* len(arr)
    #left = []
    right = [1]* len(arr)
    result = [] 
    j = len(arr)-1 
    for i in range(len(arr)):
        if i != 0:
            left[i] = left[i-1]*arr[i-1]
        if j != len(arr)-1:
            right[j]= (right[j+1]*arr[j+1])
        j -= 1 
    print(f"left: {left}, right: {right}")

    for i in range(len(left)):
        result.append(left[i]*right[i])
    return result

print(product_except_self2([1,2,0,4,5]))
print(product_except_self2([2,3,4,5]))

print(f"************O(n) space complexity, prefix/suffix pattern******************")
def product_except_self3(arr):
    result = [1]* len(arr) 
    for i in range(1, len(arr)):
        result[i] = result[i-1]*arr[i-1]
    
    right = 1
    for i in range(len(arr) - 2, -1, -1):
        right *= arr[i+1]
        result[i]= (right * result[i])

    return result

print(product_except_self3([1,2,0,4,5]))
print(product_except_self3([2,3,4,5]))
