from collections import defaultdict

def missing_number(nums):
    num_dict = defaultdict(int)
    for i, n in enumerate(nums):
        num_dict[n] = i
    for i in range(len(nums) + 1):
        if i not in num_dict:
            return i

print(missing_number([9,6,4,2,3,5,7,0,1]))
print(missing_number([3,0,2,1]))

def missing_number2(nums):
    n = len(nums)
    expected = n * (n + 1) // 2
    return expected - sum(nums)

missing_number2([3,0,2,1])    # 4 ✓
missing_number2([9,6,4,2,3,5,7,0,1])    # 8 ✓