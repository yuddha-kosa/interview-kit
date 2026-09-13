def char_pair_matcher(str):
    result = []
    for i in range(len(str)-1):
        for j in range(i+1, len(str)):
            if str[i] == str[j]:
                if (j-i)%2 == 0:
                    result.append((i, j))
    print(result)
    return (len(result))



s = "abab"
s2 = "aaaa"

print(char_pair_matcher("abab"))
#print(char_pair_matcher(s2))

def char_pair_matcher1(str):

    freq = {}
    count = 0
    for i in range(len(str)):
        if str[i] in freq:
            even, odd = freq[str[i]]
            if i%2 == 0:
                if even > 0:
                    count += even
            else:
                if odd > 0:
                    count += odd
        if i % 2 == 0:
            even, odd = freq.get(str[i], (0,0))
            freq[str[i]] =  (even+1, odd)
        else:
            even, odd = freq.get(str[i], (0,0))
            freq[str[i]] =  (even, odd+1)
    return count

print(char_pair_matcher1("abab"))

def char_pair_matcher1(s):
    freq = {}
    count = 0
    
    for i in range(len(s)):
        char = s[i]
        
        # 1. Fetch counts if seen before, otherwise default to (0, 0)
        even, odd = freq.get(char, (0, 0))
        
        # 2. Add valid pairs to our total based on current index parity
        if i % 2 == 0:
            count += even
            freq[char] = (even + 1, odd)  # Update even count
        else:
            count += odd
            freq[char] = (even, odd + 1)  # Update odd count
            
    return count

print(char_pair_matcher1("abab"))  # Output: 2
print(char_pair_matcher1("aaaa"))  # Output: 2
