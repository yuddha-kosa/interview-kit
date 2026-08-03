seen = set()
seen.add(5)
seen.add(6)
seen.add(7)
seen.add(5)

seen.remove(5)
try:
    seen.remove(5)
except KeyError:
    pass

seen.discard(7)

for i in seen:
    print(f"seen: {i}")

num = [1,2,3,3,4,5,1]
unique = set(num)
print(f"unique: {unique}")

def unique_func(nums: list)->bool:
    seen = set()
    for num in nums:
        if num in seen:
            return True
        seen.add(num)
    return False

unq1 = unique_func([1,2,3,1])
print(f"unq1: {unq1}")
unq2 = unique_func([1,2,3,4,5])
print(f"unq2: {unq2}")

num3 = [1,2,3,4,5]
num4 = [4,5,6,7,8]

set3 = set(num3)
set4 = set(num4)

intersection = set3 & set4
print(f"intersection: {intersection}")

union = set3 | set4
print(f"union: {union}")

set3_only = set3-set4
print(f"set3_only: {set3_only}")

set4_only = set4-set3
print(f"set4_only: {set4_only}")

symmentric = set3 ^ set4
print(f"symmentric: {symmentric}")
