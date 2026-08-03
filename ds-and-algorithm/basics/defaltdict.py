from collections import defaultdict

dict = defaultdict(int)
dict["num"] = 1
dict["num2"] = 20

print(f'dict: {dict}')

dict_new = defaultdict(lambda: defaultdict(int))
dict_new["saurabh"]["prep"] = 5
dict_new["saurabh"]["work"] = 50
dict_new["saurabh"]["project"] = 1
print(f'dict: {dict_new}')

countchar = defaultdict(int)
for c in "leetcode":
   countchar[c] += 1
print(f"countchar: {countchar}")

