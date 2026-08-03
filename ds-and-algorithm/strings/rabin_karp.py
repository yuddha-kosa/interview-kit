def rabin_karp(text, pattern):

    txt_len = len(text)
    pat_len = len(pattern)
    right = 1
    current_hash = 0
    pat_hash = 0

    for i in range(pat_len):
        current_hash += ord(text[i])
    for i in range(pat_len):
        pat_hash += ord(pattern[i])
    
    if current_hash == pat_hash:
        if text[:pat_len] == pattern:
            return 0

    while right < (txt_len-pat_len+1):

        current_hash = current_hash-ord(text[right-1])+ord(text[right+pat_len-1])
        if current_hash == pat_hash:
            if text[right:right+pat_len] == pattern:
                return right
        right += 1
    return -1


def rabin_karp_multi(text, patterns):
    from collections import defaultdict

    # group patterns by length
    pattern_groups = defaultdict(dict)
    for p in patterns:
        h = sum(ord(c) for c in p)
        pattern_groups[len(p)][h] = p

    results = []

    # run separate search for each pattern length
    for m, hash_to_pattern in pattern_groups.items():
        window_hash = sum(ord(c) for c in text[:m])

        for i in range(len(text) - m + 1):
            if window_hash in hash_to_pattern:
                if text[i:i+m] == hash_to_pattern[window_hash]:
                    results.append((i, hash_to_pattern[window_hash]))

            if i + m < len(text):
                window_hash = window_hash - ord(text[i]) + ord(text[i+m])

    return results

print(rabin_karp_multi("abcdeabwxyz", ["ab", "cde", "wxyz"]))
# [(0,'ab'), (2,'cde'), (5,'ab'), (8,'wxyz')]