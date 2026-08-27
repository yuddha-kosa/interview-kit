def validWordAbbreviation(word, abbr):

    if len(word) == 0 and len(abbr) == 0:
        return True

    left = 0
    right = len(word)
    lefta = 0
    while left < right and lefta < len(abbr):
        #print(f"left word: {left}, left abb: {lefta}")
        if word[left] == abbr[lefta]:
            left += 1
            lefta += 1
        elif word[left] != abbr[lefta]:
            if abbr[lefta].isdigit() and int(abbr[lefta]) != 0:
                local = lefta
                num = 0
                count = 0
                while  abbr[local].isdigit():
                    count += 1
                    num = num*10 + int(abbr[local]) 
                    local += 1
                #print(f"num: {num}")
                #print(f"count: {count}")
                left += num
                lefta += count
                if left > right-1:
                    return False 
            else:
                return False 
    return True



word = "international"
abbr = "i9l"

print(validWordAbbreviation(word, abbr))

word1 = "apple"
abbr1 = "a3e"
print(validWordAbbreviation(word1, abbr1))

word3 = "abbreviation"
abbr3 = "abbreviation"
print(validWordAbbreviation(word3, abbr3))

word4 = "implementation"
abbr4 = "imp4n500n" 
print(validWordAbbreviation(word4, abbr4))

word5 = "implementation"
abbr5 = "i12n" 
print(validWordAbbreviation(word5, abbr5))