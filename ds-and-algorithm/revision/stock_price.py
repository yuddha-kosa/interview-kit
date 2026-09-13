def stock_price(arr):

    profit = -1
    current = 0
    left = 0

    for right in range(1, len(arr)):
        if (arr[right]-arr[left]) < 0:
            left += 1
            current = 0
        else:
            current = arr[right]-arr[left]
        
        profit = max(profit, current)
    if profit != 0:
        return profit
    else:
        return -1






print(stock_price([2,4,1,7,3,8]))
print(stock_price([10,9,8,7]))