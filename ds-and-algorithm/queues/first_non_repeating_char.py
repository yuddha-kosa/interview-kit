def first_nonrepeating_char(string):
    '''
    freq = [0]*26

    for ch in string:
        freq[ord(ch)-ord('a')] += 1

    for key, val in enumerate(freq):
        if val == 1:
            return chr(key + ord('a'))
    print(f"nonrepeating char not found...")
    return
    '''
    freq = {}
    for ch in string: 
        freq[ch] = freq.get(ch, 0) + 1
    
    for ch in string:
        if freq[ch] == 1:
            return ch
    print(f"nonrepeating char not found...")
    return
print(first_nonrepeating_char("hellothere"))
print(first_nonrepeating_char("civicservant"))

print("*************************************")
from collections import deque

def first_nonrepeating_char1(stream):
    freq = {}
    queue = deque()

    for ch in stream:
        freq[ch] = freq.get(ch, 0) + 1
        queue.append(ch)

        # remove repeating chars from front
    while queue and freq[queue[0]] > 1:
        queue.popleft()

    if queue:
        #print(f"after '{ch}': first non-repeating = {queue[0]}")
        return queue[0]

print(first_nonrepeating_char1("aabbc"))
print(first_nonrepeating_char1("hellothere"))
print(first_nonrepeating_char1("civicservant"))