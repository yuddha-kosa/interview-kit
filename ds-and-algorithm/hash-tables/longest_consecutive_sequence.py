def longest_consecutive_sequence(arr):

    seen = set(arr)
    max_len = 0

    for i in range(len(arr)):
        curr = arr[i]
        curr_len = 0

        while curr in seen:
            curr += 1
            curr_len += 1
        max_len = max(max_len, curr_len)
    return max_len


print(longest_consecutive_sequence([8,1,9,2,5,4,3]))

def longest_consecutive_sequence2(arr):

    seen = set(arr)
    max_len = 0

    #for i in range(len(arr)):
    for curr in seen:
        #curr = arr[i]
        curr_len = 0
        if curr-1 not in seen:
            while curr in seen:
                curr += 1
                curr_len += 1
        max_len = max(max_len, curr_len)
    return max_len

print(longest_consecutive_sequence2([8,1,9,2,5,4,3]))