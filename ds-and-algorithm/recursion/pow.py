def pow_r(x, n):
    
    if n == 0:    # x^0 = 1
        return 1
    if n == 1:    # x^1 = x
        return x
    
    print(f"before n: {n}, x: {x}")
    p = pow_r(x, n//2)

    #print(f"before modulo n: {n}, x: {x}, p: {p}")
    if n%2 != 0:
        return x*p*p
    print(f"n: {n}, x: {x}, p: {p}")
    return p*p


print(pow_r(2, 8))




#Example: 2^8 = (2^4)^2 = (2^2)^2)^2 = ...

def pow_r1(x, n):
    
    if n == 0:    # x^0 = 1
        return 1
    if n == 1:    # x^1 = x
        return x
    
    return x*pow_r1(x,n-1)
print(pow_r1(2, 8))