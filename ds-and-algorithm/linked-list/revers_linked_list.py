class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):

    if not head:
        print("list is empty...")
        return
    
    if head.next == None:
        return head
    
    previous = None

    current = head

    while current:
        real_next = current.next
        current.next = previous
        previous = current
        current = real_next
    return previous


# Build linked list: 1→2→3→4→5
head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(5)

result = reverse_list(head)

# Print result
current = result
while current:
    print(current.val, end=" → ")
    current = current.next