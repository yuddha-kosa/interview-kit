class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reorder_list(head):

    if not head:
        return
    
    fast = head
    slow = head

    # find mid
    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next
    
    # reverse after the mid
    previous = None
    current = slow.next
    slow.next = None # cut the list in half
    while current:
        next_node = current.next
        current.next = previous
        previous = current
        current = next_node

    # merge both first and second part
    first_half = head
    second_half = previous
    while first_half and second_half:
        next_node_fh = first_half.next 
        first_half.next = second_half

        next_node_sh = second_half.next
        second_half.next = next_node_fh

        first_half = next_node_fh
        second_half = next_node_sh
    return head 


head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(5)
#1->5->2->4->3

new_head = reorder_list(head)

itr = new_head
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")