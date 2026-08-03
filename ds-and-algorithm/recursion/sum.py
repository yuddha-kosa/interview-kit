def sum_of_dig(num):

    if num == 1:
        return 1
    if num <= 0:
        return 0
    return num + sum_of_dig(num-1)

print(sum_of_dig(5))

print("********************")

def sum_of_nums(nums):

    if nums < 10:
        return nums
    r = nums%10
    q = nums//10
    return r+sum_of_nums(q)

print(sum_of_nums(103456))
# 1+0+3+4+5+6

print("********************")

def sum_of_nums1(nums):
    sum_n = 0
    while nums >= 10:
        r = nums%10
        nums = nums//10
        sum_n = sum_n+r
    sum_n = sum_n + nums
    return sum_n


print(sum_of_nums1(103456))

'''
print("********************")
def reverse(nums):
    if nums < 10:
        return nums
    r = nums%10
    q = nums//10
    num = reverse(q) 
    print(f"r: {r}, q: {q}, {str(r)}")
    return str(r) + str(num)
    #return int("".join([str(r), str(num)]))

print(reverse(103456))

print("********************")
def reverse1(nums):
    res = []
    while nums >= 10:
        r = nums%10
        nums = nums//10
        res.append(str(r))
    res.append(str(nums))
    return int("".join(res))

print(reverse1(103456))
'''