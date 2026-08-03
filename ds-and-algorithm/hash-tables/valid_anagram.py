def valid_anagram(txt1,txt2):

    hash_text1 = {}
    hash_text2 = {}

    for ch in txt1:
        hash_text1[ch] = hash_text1.get(ch, 0) + 1
    
    for ch in txt2:
        hash_text2[ch] = hash_text2.get(ch, 0) + 1

    if len(hash_text1) != len(hash_text2):
        return False
    
    for key, val in hash_text2.items():
        if key not in hash_text1 or val != hash_text1[key]:
            return False
    return True

print(valid_anagram("listen", "silent"))
print(valid_anagram("hello", "world"))

def valid_anagrami2(txt1, txt2):
    if len(txt1) != len(txt2):
        return False
    count = {}
    for ch in txt1:
        count[ch] = count.get(ch, 0) + 1
    for ch in txt2:
        count[ch] = count.get(ch, 0) - 1
        if count[ch] < 0:
            return False
    return True

def valid_anagram3(txt1, txt2):
    if len(txt1) != len(txt2):
        return False

    count = [0] * 26    # index 0=a, 1=b, ... 25=z

    for i in range(len(txt1)):
        count[ord(txt1[i]) - ord('a')] += 1    # increment for txt1
        count[ord(txt2[i]) - ord('a')] -= 1    # decrement for txt2

    #return all(c == 0 for c in count)    # all zeros = anagram
    for c in count:
        if c != 0:
            return False
    return True