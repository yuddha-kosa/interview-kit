'''
&  (AND):  1 only if BOTH bits are 1
|  (OR):   1 if EITHER bit is 1

^  (XOR):  1 if the bits are DIFFERENT (exactly one is 1)
XOR (^) — 1 if the bits are DIFFERENT
a     = 1101 (13)
b     = 1011 (11)
a^b   = 0110 (6)
bit by bit:
  1^1 = 0  (same -> 0)
  1^0 = 1  (different -> 1)
  0^1 = 1  (different -> 1)
  1^1 = 0  (same -> 0)

~  (NOT):  flips every bit (0→1, 1→0)
<< (left shift):  shifts bits LEFT, filling with 0s (multiplies by 2 per shift)
>> (right shift): shifts bits RIGHT (divides by 2 per shift, roughly)
'''
import math

def binary_to_int(binary):
    length = len(binary)
    num = 0 

    for i in range(length):
        #num += int(binary[i]) * (math.pow(2, length-i-1))
        num += int(binary[i]) * (2 ** (length-i-1))
    
    return num

print(binary_to_int("11111010"))

# old number × 2 + new digit
def binary_to_int1(binary):
    num = 0

    for ch in binary:
        print("num << 1: ", num << 1)
        num = (num << 1) | int(ch)
    
    return num


print(binary_to_int1("11111010"))

'''
Time:  O(n)
Space: O(1)
'''

def int_to_binary(num):

    if num == 0:
        return "0"

    binary = ""

    while num > 0:
        rem = num%2
        binary = str(rem) + binary
        num = num//2

    return binary

print(int_to_binary(13))

'''
Time:  O(log n) — the number of digits in n's binary
       representation is proportional to log2(n)
Space: O(log n) — the output string length
'''

def test():
    num1 = 1010
    num2 = 1011

    print("num1&1", num1 & 1)
    print("num2&1", num2 & 1)
    print("num2&num1", num2 & num1)
    print("num1&num2", num1 & num2)

    print("num1|1", num1 | 1)
    print("num2|1", num2 | 1)
    print("num1|num2", num1 | num2)

test()