'''
WRONG
def eval_rpn(root):
    stack = []
    #valid_operators = ["+","-","*","/"]
    valid_operators = {"+":"+", "-":"-", "*":"*", "/":"/"}
    for char in root:
        if char in valid_operators:
            if stack:
                print(f"stack before valid operators: {stack}")
                if valid_operators[char] == "+":
                    result = 0
                    while stack:
                        result = result + stack.pop()
                elif valid_operators[char] == "-":
                    result = stack.pop()
                    while stack:
                        result = result-stack.pop()
                elif valid_operators[char] == "*":
                    result = 1
                    while stack:
                        result = result * stack.pop()
                elif valid_operators[char] == "/":
                    result = stack.pop()
                    while stack:
                        result = result // stack.pop()
                else:
                    print(f"invalid operator: {char}")
                    return
                print(f"stack after valid operators: {stack}")
                stack.append(result)
        else:
            num = int(char)
            stack.append(num)
            print(f"stack after append: {stack}")
    return result
                

print(eval_rpn(["2","1","+","3","*"]))
print(eval_rpn(["10","6","9","3","+","-11","*","/","*","17","+","5","+"]))
'''

def eval_rpn(tokens):
    stack = []

    for token in tokens:
        if token in "+-*/":
            b = stack.pop()    # second operand
            a = stack.pop()    # first operand

            if token == "+":
                stack.append(a + b)
            elif token == "-":
                stack.append(a - b)
            elif token == "*":
                stack.append(a * b)
            elif token == "/":
                stack.append(int(a / b))    # truncate toward zero
        else:
            stack.append(int(token))

    return stack[0]

print(eval_rpn(["2","1","+","3","*"]))    # 9
print(eval_rpn(["4","13","5","/","+"])) # 6