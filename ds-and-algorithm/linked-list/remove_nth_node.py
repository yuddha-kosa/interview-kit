class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def remove_nth(head, nth):

    if not head:
        return
    
    count = 0
    current_del = head
    diff = -nth
    current = head

    while current:
        diff = count-nth
        if diff >= 0:
            prev_node_to_del = current_del
            current_del = current_del.next
            print(f"diff: {diff}, count: {count}, prev_node_to_del: {prev_node_to_del}")
        count += 1
        current = current.next
    
    if diff == -1:
        head = current_del.next
        print(f"head: {head}")
        return head
    if diff >= 0:
        #next_node = prev_node_to_del.next.next
        prev_node_to_del.next = prev_node_to_del.next.next 
    else:
        print("nth element not found in the list node")
        return

    return head

head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(5)

result = remove_nth(head, 3)

# Print result
current = result
while current:
    print(current.val, end=" →")
    current = current.next

print("\n********")
head1 = ListNode(1)

result1 = remove_nth(head1, 1)

# Print result
current1 = result1
while current1:
    print(current1.val, end=" → ")
    current1 = current1.next


def remove_nth1(head, n):
    dummy = ListNode(0)    # dummy node before head
    dummy.next = head
    fast = dummy
    slow = dummy

    # move fast n+1 steps ahead
    for _ in range(n + 1):
        fast = fast.next

    # move both until fast is None
    while fast:
        fast = fast.next
        slow = slow.next

    # remove nth node
    slow.next = slow.next.next

    return dummy.next    # head might have changed