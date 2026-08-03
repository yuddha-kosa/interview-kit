def longest_sequence(arr):

    seen = set(arr)
    max_seq = 0
    for i in range(len(arr)):
        num = arr[i]
        current = 0
        if num-1 not in seen:
            while num in seen:
                current += 1
                num += 1
        max_seq = max(max_seq, current)
    return max_seq

print(longest_sequence([8,1,9,2,5,4,3]))