class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def sort_list(head):

    # recursion exit case.
    if head == None or head.next == None:
    #if not head or not head.next:
        return head
    
    # find mid
    slow = head
    fast = head.next

    while fast and fast.next:
        fast = fast.next.next
        slow = slow.next

    head_right = slow.next
    slow.next = None

    left = sort_list(head)
    right = sort_list(head_right)

    return merge_list(left, right)



def merge_list(head1, head2):

    if head1 == None or head2 == None:
        return head1 or head2
    dummy = ListNode()
    current = dummy

    while head1 and head2:

        if head1.val <= head2.val:
            current.next = head1
            head1 = head1.next
        else:
            current.next = head2
            head2 = head2.next
        current = current.next
    
    if head1:
        current.next = head1
    if head2:
        current.next = head2
    return dummy.next




head = ListNode(-1)
head.next = ListNode(5)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(0)


result = sort_list(head)

itr = result
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")
