def kmp(text, pattern):
    n = len(text)
    m = len(pattern)

    # Step 1 — build LPS array
    lps = build_lps(pattern)

    # Step 2 — search
    i = 0    # text pointer
    j = 0    # pattern pointer

    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == m:                    # full match found
            return i - j
            j = lps[j-1]             # look for next match

        elif i < n and text[i] != pattern[j]:
            # pattern: A  B  A  B  C  A  B  A  B
            #          0  1  2  3  4  5  6  7  8
            #lps:      0  0  1  2  0  1  2  3  4
            if j != 0:
                j = lps[j-1]         # jump using LPS
            else:
                i += 1               # no prefix match, move text

    return -1


# pattern = "AABAAC"
# lps: The first k characters of the pattern are identical to
# the last k characters of the substring ending at i.
def build_lps(pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0    # length of previous longest prefix suffix
    i = 1

    # just think that 0-length as the pattern and right side towards array as the text then it
    # will look similar to the KMP algorithm itself, where we look for lps of last element if there
    # is mismatch in the current element. whatever index lps gives that we use that as the starting point
    # in our search because we know all the index before that has already been matched.
    # even here while preparing the lps when there is mismatch of the current element i with the
    # left element (current length), we try to look for lps of last element and see what lps value
    # it returns because that will tell us eif there was any existing pref-suffix, if not then it will
    # return 0 and we will match the current ith element with 0th element, otherwise whatever value lps
    # returns we will use that to match with our current ith and see if the prefix-suffix can be extended?
    # this is the beauty that even while preparing the lps array it'self we can utilize the lps list
    # prepared till know to prepare the lps for the current ith element.
    # there can be intuition that why don't we just match lenth-1 with ith element ? the reason is
    # even if length-1 matches with i that does not mean that prefix-suffix exists...we have to make sure
    # we are adding i on top of current prefix-suffix and then matching it with the initial part of the
    # pattern, so lps gives us that, if lps of last element is not 0 that means prefix-suffix pair
    # exists and we can try adding i on top of it and try matching it with the first part of the pattern
    # and see if it matches, if it matches then increase the length of prefi-suffix, otherwise we will
    # again we will reduce the size of suffix and see if it has any matching prefix ? we will keep doing
    # it until it (ith element) becomes the only suffix and element of position 0 becomes
    # the only prefix, if they also don't match we will update the lps of the ith element to 0.
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                # we are trying to see if next smallest prefix-suffix can be extended or not ??
                # length = lps[length-1]: is really saying:
                # The border of length length failed. Jump directly to the largest border inside that border.
                # This recursive border-jumping is what makes KMP run in O(n) instead of repeatedly trying all smaller lengths.
                # Think of length as a left pointer here after lps gets assigned, basically we are saying that
                # length number of prefix-suffix exists and use that as the left pointer and try matching
                # char after that with the current chaar in the right(i.e i).
                # if it matches then the length of prefix-suffix will increase otherwise, next lps will
                # give the next smallest and same thing will be checked this will be done until no prefix-suffix is
                # left and finally current char will be matched with the length=0 char and if that also does not match
                # then lps of curret i will be set to 0.
                length = lps[length-1]    # fall back
            else:
                lps[i] = 0
                i += 1

    return lps

'''
Mismatch at i, j:
    j = lps[j-1]
    i stays at current position
    
    Everything before i is either:
    1. Already matched (part of valid prefix via lps)
    2. Proven to not be a valid start (via lps analysis)
    
    So i never needs to go back — ever.


    i only moves:
    Forward by 1 when match ✓
    Forward by 1 when j==0 and mismatch ✗
    STAYS when j>0 and mismatch ✗

i NEVER moves backward.
This is the O(n) guarantee of KMP.
'''

'''
AABAA

Prefixes: "A", "AA", "AAB", "AABA"
Suffixes: "A", "AA", "BAA", "ABAA"

"A"    == "A"?    Yes ✓ length=1
"AA"   == "AA"?   Yes ✓ length=2
"AAB"  == "BAA"?  No
"AABA" == "ABAA"? No

lps[4] = 2    ← longest is "AA"
'''