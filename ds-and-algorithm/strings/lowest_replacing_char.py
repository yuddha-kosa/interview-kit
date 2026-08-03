'''
"the string became invalid after adding right
 means something needs to come out
 we moved left
 checked after adding next right — is it valid now?
 if valid → string increases
 if not → something is still making it invalid
 any valid window would be smaller than current
 so we don't need to fully fix — we already captured the best"

 "We only care about windows LARGER than what we've seen.
 Sliding maintains size — fully fixing would shrink it."
'''


def lowest_replacing_char(text, k):

    max_len = 0

    freq = {}

    max_freq = 0

    left = 0

    for right in range(len(text)):

        freq[text[right]] = freq.get(text[right], 0) + 1

        max_freq = max(max_freq, freq[text[right]])

        while (right-left+1)-max_freq > k:
            freq[text[left]] -= 1
            left += 1
        
        max_len = max(max_len, (right-left+1))
    return max_len

print(lowest_replacing_char("aabcbba", 2))
print(lowest_replacing_char("XYZXYZ", 3))

'''
# Wrong approach
while window_invalid:
    count[s[left]] -= 1
    left += 1
    max_freq = max(count.values())    # O(26) extra work
'''