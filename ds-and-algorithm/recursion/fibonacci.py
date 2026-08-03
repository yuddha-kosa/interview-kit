def fibonacci(num, res):
    if num in res:
        return res[num]
    if num == 1 or num == 0:
        #print(f"fib({num}) = {1}")
        return 1

    fib = fibonacci((num-1), res) + fibonacci((num-2), res) 
    res[num] = fib
    print(f"fib({num}) = {fib}")
    return res[num]
    

print(fibonacci(6, {}))

def fibonacci1(num):
    if num == 1 or num == 0:
        #print(f"fib({num}) = {1}")
        return 1

    fib = fibonacci1((num-1)) + fibonacci1((num-2)) 
    return fib
    

print(fibonacci1(6))

'''
 fib(6)
├── fib(5)
│   ├── fib(4)
│   │   ├── fib(3)
│   │   │   ├── fib(2)
│   │   │   │   ├── fib(1)
│   │   │   │   └── fib(0)
│   │   │   └── fib(1)
│   │   └── fib(2)
│   │       ├── fib(1)
│   │       └── fib(0)
│   └── fib(3)
│       ├── fib(2)
│       │   ├── fib(1)
│       │   └── fib(0)
│       └── fib(1)
└── fib(4)
    ├── fib(3)
    │   ├── fib(2)
    │   │   ├── fib(1)
    │   │   └── fib(0)
    │   └── fib(1)
    └── fib(2)
        ├── fib(1)
        └── fib(0)
'''