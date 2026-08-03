

'''
1. What is the constraint?
   → no duplicates, sum <= k, at most k distinct chars

2. When is the constraint violated?
   → duplicate found, sum > k, distinct chars > k
   -> once constraint found shrink the window size.

3. What do you track in the window?
   → set for uniqueness, dict for counts, running sum
'''


def longest_substring(text):

    left = 0
    seen = set()
    max_len = 0

    for right in range(len(text)):
        while text[right] in seen:
            seen.remove(text[left])
            left += 1
        seen.add(text[right])
        max_len = max(max_len, len(seen))
    return max_len

        

print(longest_substring("dvdf"))
print(longest_substring("abccba"))
print(longest_substring("aaaaa"))
print(longest_substring("xyzabcxy"))
print(longest_substring("abcaaad"))


print("**************************")

def longest_substring1(text):

    left = 0
    seen = {}
    max_len = 0

    for right in range(len(text)):
        if text[right] in seen and seen[text[right]] >= left: # on constraint we are shrinking the window size.
            left = seen[text[right]] + 1 
        seen[text[right]] = right
        max_len = max(max_len, right-left+1)
    return max_len


print(longest_substring1("dvdf"))
print(longest_substring1("abccba"))
print(longest_substring1("aaaaa"))
print(longest_substring1("xyzabcxy"))
print(longest_substring1("abcaaad"))