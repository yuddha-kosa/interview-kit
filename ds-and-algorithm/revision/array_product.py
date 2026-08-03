def array_product(arr):

    left_product = []
    right_product = [0]*(len(arr))

    curr_lef_pdct = 1
    left_product.append(1)
    for i in range(1, len(arr)):
        curr_lef_pdct *= arr[i-1]
        left_product.append(curr_lef_pdct)

    curr_rht_pdct = 1
    right_product[len(arr)-1] = 1
    for i in range(len(arr)-2, -1, -1):
        curr_rht_pdct *= arr[i+1]
        right_product[i]=curr_rht_pdct
    
    final_product = []
    for i in range(len(left_product)):
        final_product.append(left_product[i]*right_product[i])
    
    return final_product


print(array_product([2,3,4,5]))


def array_product2(arr):

    result = [1]*(len(arr))

    for i in range(1, len(arr)):
        result[i] = result[i-1]*arr[i-1]

    current = 1
    for i in range(len(arr)-2, -1, -1):
        current *= arr[i+1]
        result[i] = result[i]*current
    
    
    return result


print(array_product2([2,3,4,5]))