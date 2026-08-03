def valid_anagram(txt1,txt2):

    count = {}

    for ch in txt1:
        count[ch] = count.get(ch, 0) + 1
    for ch in txt2:
        count[ch] = count.get(ch,0) - 1
        if count[ch] < 0:
            return False
    return True

print(valid_anagram("listen", "silent"))
print(valid_anagram("hello", "world"))


def valid_anagram1(txt1,txt2):

    count = [0]*26

    for i in range(len(txt1)):
        count[ord(txt1[i])-ord('a')] += 1
        count[ord(txt2[i])-ord('a')] -= 1
    for c in count:
        if c != 0:
            return False
    return True


print(valid_anagram1("listen", "silent"))
print(valid_anagram1("hello", "world"))