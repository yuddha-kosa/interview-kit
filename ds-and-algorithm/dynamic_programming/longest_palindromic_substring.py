def longest_palindromic_substring(text):
    if not text:
        return
    longest_substr = text[0]
    for i in range(len(text)-1):
        for j in range(i+1, len(text)):
            sub_str = text[i:j+1]
            if is_palindrome(sub_str):
                if len(longest_substr) < len(sub_str):
                    longest_substr = sub_str
    return longest_substr


def is_palindrome(text):

    left = 0
    right = len(text)-1
    while left < right:
        if not text[left].isalnum():
            left += 1 
        elif not text[right].isalnum():
            right -= 1
        
        else:
            if text[left] != text[right]:
                return False
            left += 1
            right += -1
    return True

print(longest_palindromic_substring("racecarfun"))


def longest_palindromic_substring_dp(text):
    n = len(text)
    left = 0
    right = 0
    # initialize table
    table = [[False]*n for _ in range(n)]
    # base cases
    # 1. every letter is a palindrome
    for i in range(n):
        table[i][i] = True
        left = i
        right = i
    # 2. if letter and it's next letter is same then it's a palindrome
    for i in range(n-1):
        if text[i] == text[i+1]:
            table[i][i+1] = True
            left = i
            right = i+1
        else:
            table[i][i+1] = False
    
    for l in range(3, n+1):
        for i in range(n-l+1):
            j = i+l-1
            if text[i] == text[j] and table[i+1][j-1]:
                table[i][j] = True
                left = i
                right = j
            else:
                table[i][j] = False

    return text[left:right+1]

print(longest_palindromic_substring_dp("racecarfun"))
print(longest_palindromic_substring_dp("baab"))

'''
Time:  O(n²)
Space: O(n²) 
'''