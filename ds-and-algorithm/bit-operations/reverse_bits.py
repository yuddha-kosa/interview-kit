def reverse_bits(num):

    reverse = 0
    for _ in range(32):
        # step 1: find the least significant bit.
        least_significat_bit = num&1
        # step 2: shift the current reverse to left and create a new space on the right.
        reverse = reverse << 1
        print("reverse before", reverse)
        print("binary r",bin(reverse))
        # step 3: add the least significant bit to the reverse result. 
        reverse = reverse | least_significat_bit
        print("reverse after", reverse)

        # step 4: right shift and let go the current least significant bit
        num >>= 1
        print("*********")
    print(bin(reverse))
    return reverse


print(reverse_bits(0b00000010100101000001111010011100))