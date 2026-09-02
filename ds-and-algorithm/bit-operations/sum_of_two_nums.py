def sum_of_two_nums1(a, b):
    sum = a^b
    carry = a&b
    carry = carry << 1

    while carry != 0:
        temp = sum
        sum = sum^carry
        carry = temp&carry
        carry = carry << 1

    return sum


print(sum_of_two_nums1(3,5))
print(sum_of_two_nums1(6,9))
print(sum_of_two_nums1(16,19))


def sum_of_two_nums(a, b):
    while b != 0:
        carry = (a&b) << 1
        a = a^b
        b = carry

    return a

print(sum_of_two_nums(3,5))
print(sum_of_two_nums(6,9))
print(sum_of_two_nums(16,19))

'''

Time:  O(log(max(a,b))) — carry propagation takes at most as
       many steps as there are BITS in the larger number
Space: O(1)

time: O(1)
space: O(1)
'''