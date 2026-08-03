class Stack:
    def __init__(self):
        self.stack = []
    
    def is_empty(self):
        if len(self.stack) == 0:
            return True
        return False

    def push(self, val):
        self.stack.append(val)
    
    def pop(self):
        if self.is_empty():
            print("stack is empty...")
            return
        return self.stack.pop()
    
    def peek(self):
        if self.is_empty():
            print("stack is empty...")
            return
        return self.stack[-1]
    
    def size(self):
        return len(self.stack)

    def clear(self):
        return self.stack.clear()
