def num_of_one_bits(n):
    count = 0
    while n:
        count += n&1

        n >>= 1

    return count
        



print(num_of_one_bits(0b0000000000000011010))
print(num_of_one_bits(0b11010))
print(num_of_one_bits(int("11010", 2)))