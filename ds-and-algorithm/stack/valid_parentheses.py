def is_valid(expr):
    stack = []

    for char in expr:
        if char == "{" or char == "[" or char == "(":
            stack.append(char)
        elif char == "}" or char == "]" or char == ")":
            if char == "}":
                if not stack or stack[-1] != "{":
                    return False
                stack.pop()
            elif char == "]":
                if not stack or stack[-1] != "[":
                    return False
                stack.pop()
            elif char == ")":
                if not stack or stack[-1] != "(":
                    return False
                stack.pop()
        else:
            print(f"invalid char in exp: {char}")
            return

    if len(stack) == 0:
        return True
    print(f"stack: {stack}")
    return False

print(is_valid("()"))
print(is_valid("{[]}]"))
print(is_valid("{[]}"))
print(is_valid("{}[]()"))

def is_valid1(expr):
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}

    for char in expr:
        if char in "({[":
            stack.append(char)
        elif char in ")}]":
            if not stack or stack[-1] != pairs[char]:
                return False
            stack.pop()

    return len(stack) == 0