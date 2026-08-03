def stock_trade(arr):
    current = arr[0]
    max_profit = 0

    #for i in range(1, len(arr)):
    for i in range(len(arr)-1):
        current_profit = arr[i+1]-current
        max_profit = max(max_profit, current_profit)
        if current > arr[i+1]:
            current = arr[i+1]
    return max_profit


print(stock_trade([2,4,1,7,3,8]))
print(stock_trade([10,9,8,7]))