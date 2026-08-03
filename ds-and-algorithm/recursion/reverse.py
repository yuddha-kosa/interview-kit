
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