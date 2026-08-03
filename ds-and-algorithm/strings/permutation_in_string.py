'''
1. Build initial window of size k
2. Check initial window
3. Loop from k to end:
   - add right element
   - remove left element (index i-k)
   - check window
'''
def permutation_in_string(txt1,txt2):

    txt1_freq = {}
    txt2_freq = {}

    for ch in txt1:
        txt1_freq[ch] = txt1_freq.get(ch, 0) + 1

    window_len = len(txt1)

    for i in range(window_len):
        txt2_freq[txt2[i]] = txt2_freq.get(txt2[i], 0) + 1

    if txt1_freq == txt2_freq:
        return True
    
    for i in range(window_len, len(txt2)):
        found = True

        # update frequency hash
        txt2_freq[txt2[i]] = txt2_freq.get(txt2[i], 0) + 1    
        # shrink the window and create new window
        txt2_freq[txt2[i-window_len]] -= 1
        if txt2_freq[txt2[i-window_len]] == 0:
            del txt2_freq[txt2[i-window_len]]

        # we can directly compare two maps in python.
        #if txt1_freq == txt2_freq:
        #    return True
        for key, val in txt1_freq.items(): 
            if key not in txt2_freq or val != txt2_freq[key]:
                found = False
                break
        
        if found:
            return True
    return False

print(permutation_in_string("abc", "eidcabooo"))
print(permutation_in_string("xyz", "abcdef"))

