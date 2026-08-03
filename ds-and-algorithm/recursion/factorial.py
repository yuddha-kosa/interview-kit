def factorial(num):

    if num <= 1:
        return 1
    f = factorial(num-1)
    return num*f
    #return num*factorial(num-1)



print(factorial(5))