class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def is_palindrome(head):
    if not head:
        return True

    fast = head
    slow = head

    count = 0
    # find mid, slow willbe mid
    while fast:
        if count > 0 and count%2 == 0:
            slow = slow.next
        count += 1
        fast = fast.next
    
    rev = slow.next
    tail = slow
    # reverse just after mid, we will use mid later to rever back
    while rev:
        next_node = rev.next
        rev.next = tail
        tail = rev
        rev = next_node
    
    left = 0
    right = count-1
    left_head = head
    right_tail = tail
    while left <= right:
        if left_head.val != right_tail.val:
            return False
        left_head = left_head.next 
        right_tail = right_tail.next
        left += 1
        right -= 1
    
    curr = tail
    prev = None
    while curr != slow:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    
    itr = head
    while itr:
        #print(itr.val)
        print(itr.val, end=" → ")
        itr = itr.next
    print("\n")

    return True


head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(2)
head.next.next.next.next = ListNode(1)

itr = head
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")
print(is_palindrome(head))

def is_palindrome(head):
    # Step 1 — find middle
    fast = head
    slow = head
    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next

    # Step 2 — reverse second half
    prev = None
    curr = slow
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node

    # Step 3 — compare both halves
    left = head
    right = prev    # head of reversed second half

    while right:    # second half is shorter for even list and larger for odd list.,but left always
        # kept pointing to the mid...while comparing it will be of equal length.
        if left.val != right.val:
            return False
        left = left.next
        right = right.next
        
    prev2 = None
    curr = prev
    while curr:
        next_node = curr.next
        curr.next = prev2
        prev2 = curr
        curr = next_node

    return True                                    