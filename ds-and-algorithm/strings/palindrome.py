def is_palindrome(txt):
    left = 0
    right = len(txt)-1

    while left < right:
        while left < right and not txt[left].isalnum():
            #print(f"skipping left: {txt[left]}")
            left += 1
        left_txt = txt[left].lower()

        while left < right and not txt[right].isalnum():
            #print(f"skipping right: {txt[right]}")
            right -= 1
        right_txt = txt[right].lower()

        if left >= right:
            break
        #print(f"left: {left_txt}, right: {right_txt}")
        if left_txt != right_txt:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("Was it a car or a cat I saw?"))
print(is_palindrome("hello world"))
print(is_palindrome('txt = "!@#$"'))
print(is_palindrome("!@#$"))
print(is_palindrome("No lemon, no melon"))

print("*******************")
def is_palindrome1(txt):
    left = 0
    right = len(txt)-1

    while left < right:
        if not txt[left].isalnum():
            left += 1
        elif not txt[right].isalnum():
            right -= 1
        else:
            if txt[left].lower() != txt[right].lower():
                return False
            left += 1
            right -= 1
    return True
            
print(is_palindrome("Was it a car or a cat I saw?"))
print(is_palindrome("hello world"))
print(is_palindrome('txt = "!@#$"'))
print(is_palindrome("!@#$"))
print(is_palindrome("No lemon, no melon"))
print(is_palindrome("a"))