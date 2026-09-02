
# we will loop and write a method to convert in binary.
# we will write a method to count 1 by using the 1 & operation
# with the least significant bit and shift right by 1.

def to_binary(n):
    if n == 0:
        return "0"
    binary = ""
    while n > 0:
        mod = n%2
        binary = str(mod)+binary
        n = n//2
    return binary

def count_one(binary):
    count = 0
    while binary:
        count += binary&1
        binary = binary >> 1
    return count

def counting_bits(num):
    result = []

    for i in range(num+1):
        b = to_binary(i)
        c = count_one(int(b,2))

        #c = count_one(i)
        result.append(c)
    return result


print(counting_bits(5))

'''
time: O(n log n)
space: O(n)
'''


'''
Every number can be written as: (the LARGEST power of 2 that
fits inside it) + (some remainder).

The number of 1-bits in that number = 1 (for that power-of-2
bit) + (however many 1-bits are in the REMAINDER).

Since the remainder is ALWAYS SMALLER than the current number,
we can look up its bit-count from something we ALREADY computed.

Concrete example — building up understanding:

7  = 4 + 3     -> bits(7) = 1 + bits(3)
6  = 4 + 2     -> bits(6) = 1 + bits(2)
5  = 4 + 1     -> bits(5) = 1 + bits(1)
4  = 4 + 0     -> bits(4) = 1 + bits(0)   (4 itself IS a power of 2)
'''

def counting_bits_dp(num):
    mem = [0]*(num+1)
    offset = 1
    for i in range(1, num+1):
        if i == (offset*2):
            offset = i
        mem[i] = 1 + mem[i-offset]
    return mem

print(counting_bits_dp(6))

'''
time: O(n)
space: O(n)
'''