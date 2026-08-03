
def fib(num, mem={}):
    if num in mem:
        return mem[num]
    if num == 0:
        print(f"0")
        return 0
    if num == 1:
        print(f"t:1")
        return 1
    
    mem[num] = fib(num-1, mem) + fib(num-2, mem)
    print(f"{mem[num]}")
    return mem[num]

fib(8)