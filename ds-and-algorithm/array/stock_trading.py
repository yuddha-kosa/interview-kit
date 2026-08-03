def max_profit(arr):
    max_profit = 0
    for i in range(len(arr)-1):
        for j in range(i+1, len(arr)):
            current_profit = arr[j]-arr[i]
            max_profit = max(current_profit, max_profit)

    return max_profit

print(max_profit([2,4,1,7,3,8]))
print(max_profit([10,9,8,7]))
print(max_profit([2,1,7]))

print("*******************")


# create one pointer smallest and move it after comparing it with the next element.
# if the next element is smaller than the smallest than the next element will become the smallest.
# and then use smallest to calculate the current profit and compare it with the current max and
# accordingly update the max profit.
def max_profit1(arr):
    smallest = arr[0]
    max_profit = 0

    for i in range(1, len(arr)):
        #smallest = min(smallest, arr[i])
        current_profit = arr[i] - smallest
        max_profit = max(max_profit, current_profit)
        smallest = min(smallest, arr[i])
    
    return max_profit


print(max_profit1([2,4,1,7,3,8]))
print(max_profit1([10,9,8,7]))
print(max_profit1([2,1,7]))