def longest_sub_str_without_repeating_char(txt):

    freq = {}
    left = 0
    max_len = 0

    for right in range(len(txt)):
        if txt[right] in freq and freq[txt[right]] >= left:
            left = freq[txt[right]]+1
        freq[txt[right]] = right
        max_len = max(max_len, (right-left+1))
    return max_len

print(longest_sub_str_without_repeating_char("abccba"))
print(longest_sub_str_without_repeating_char("xyzabcxy"))