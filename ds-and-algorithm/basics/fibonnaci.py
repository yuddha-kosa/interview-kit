
'''
def fibonnaci(num):
    #start = 0
    #next = 1
    series = []
    for i in range(num):
        if i == 0:
            series.append(i)
        elif i == 1:
            series.append(i)
        else:
            current = series[i-1]+series[i-2]
            series.append(current)

    return series


series = fibonnaci(8)
print(f"series: {series}")
'''

def fib(n, memo={}):
    if n in memo:
        return memo[n]      # return cached result

    if n == 0: return 0
    if n == 1: return 1

    memo[n] = fib(n-1, memo) + fib(n-2, memo)
    return memo[n]


series = fib(8, {})
print(f"series: {series}")