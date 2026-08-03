class Node:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class SingleLinkedList:
    def __init__(self):
        self.head = None
    
    def length(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

    def search(self, target):
        current = self.head
        count = 0
        while current:
            if current.val == target:
                return count
            count += 1
            current = current.next 
        return -1
    
    def insert_at_start(self, val):
        node = Node(val)
        node.next = self.head
        self.head = node
    
    def insert_at_pos(self, val, pos):
        node = Node(val)
        if pos == 0:
            node.next = self.head
            self.head = node
            return
        current = self.head
        count = 0
        while current and count < pos-1:
            count += 1
            current = current.next
        
        node.next = current.next
        current.next = node
    
    def insert_at_end(self, val):
        node = Node(val)
        if not self.head:
            self.head = node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = node

    def delete_tail(self):
        if not self.head:
            print("empty list...")
            return
        current = self.head
        if current.next == None:
            self.head = None
            return

        while current.next.next:
            current = current.next
        
        current.next = None
    
    def delete_head(self):
        if not self.head:
            print("empty list...")
            return
        current = self.head
        self.head = current.next
    
    def delete_val(self, val):
        if not self.head:
            print("empty list...")
            return
        current = self.head
        if current.val == val:
            self.head = current.next
            return
        
        while current:
            if current.next.val == val:
                current.next = current.next.next
                return
            current = current.next
        
    
    def print_list(self):
        if self.head == None:
            print("empty list...")
            return
        current = self.head
        while current:
            print(f"current val: {current.val}")
            current = current.next



        

sl = SingleLinkedList()
sl.insert_at_start(2) 
sl.insert_at_start(4)
sl.insert_at_pos(5, 1)
sl.print_list()
print("*************")
sl.delete_val(5)
sl.print_list()