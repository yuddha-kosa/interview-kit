def build_lps(pattern):

    size = len(pattern)
    right = 1
    lps = [0] * size
    left = 0 # treat this as pointer and length of largest prefix-suffix.

    while right < size:

        if pattern[left] == pattern[right]:
            left += 1
            lps[right] = left
            right += 1
        else:
            if left != 0:
                left = lps[left-1]
            else:
                lps[right] = 0
                right += 1
    return lps

def kmp(text, pattern):

    text_len = len(text)
    pat_len = len(pattern)
    lps = build_lps(pattern)
    i = 0 # tracks text
    j = 0 # tracks pattern
    while i < text_len:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        if j == pat_len:
            return i-j
        elif text[i] != pattern[j]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return -1
        



