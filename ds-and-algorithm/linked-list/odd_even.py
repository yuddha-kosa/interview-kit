class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
'''
def odd_even(head):
    if not head:
        return head
    odd = head
    even = head.next
    old_even = head.next

    while(odd and odd.next) and (even and even.next):
        odd_next_node = odd.next.next
        even_next_node = even.next.next

        odd.next = odd_next_node 
        even.next = even_next_node 

        odd = odd_next_node
        even = even_next_node

    if odd and odd.next:
        odd_next_node = odd.next.next
        odd.next = odd_next_node 
        odd = odd_next_node 

    if even and even.next:
        even_next_node = even.next.next
        even.next = even_next_node 
        even = even_next_node 

    odd.next = old_even   
    return head
'''

def odd_even(head):
    if not head:
        return head
    odd = head
    even = head.next
    even_head = head.next

    while even and even.next:
        odd.next = even.next
        odd = odd.next
        even.next = odd.next
        even = even.next
    odd.next = even_head
    return head

head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(5)
#1->3->5->2->4

new_head = odd_even(head)

itr = new_head
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")