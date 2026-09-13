def permutation_in_string(st1, st2):
    k = len(st1)
    left = 0
    freq_st1 = [0]*26
    curr_freq = [0]*26

    for ch in st1:
        freq_st1[ord(ch)-ord('a')] += 1

    for ch in st2[:3]:
        curr_freq[ord(ch)-ord('a')] += 1
    if curr_freq == freq_st1: 
        return True

    for right in range(k, len(st2)):
       curr_freq[ord(st2[right])-ord('a')] += 1 
       curr_freq[ord(st2[left])-ord('a')] -= 1
       left += 1
       if curr_freq == freq_st1: 
          return True
    return False

print(permutation_in_string("abc", "eidcabooo"))
print(permutation_in_string("xyz", "abcdef"))

