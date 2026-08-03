class MinStack:
    def __init__(self):
        self.min_stack = []
        self.stack = []
    
    def push(self, val):
        self.stack.append(val)
        if self.min_stack:
            if val < self.min_stack[-1]:
                 self.min_stack.append(val)
            else:
                 self.min_stack.append(self.min_stack[-1])
        else:
            self.min_stack.append(val)

    def pop(self):
        if len(self.stack) == 0:
            print("min stack is empty...")
            return
        self.min_stack.pop()
        return self.stack.pop()
    
    def top(self):
        if len(self.stack) == 0:
            print("stack is empty...")
            return
        return self.stack[-1]
    
    def getMin(self):
        if len(self.min_stack) == 0:
            print("min stack is empty...")
            return
        return self.min_stack[-1]

min_stack = MinStack()
min_stack.push(-2)
min_stack.push(0)
min_stack.push(-3)
min_val = min_stack.getMin()
print(f"min_val: {min_val}")
min_stack.pop()
top_val = min_stack.top()
print(f"top_val: {top_val}")
min_val = min_stack.getMin()
print(f"min_val: {min_val}")