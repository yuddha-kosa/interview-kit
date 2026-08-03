class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_lists(l1,l2):

    if not l1 and not l2:
        return l1
    if l1 and not l2:
        return l1
    if l2 and not l1:
        return l2

    currentl1 = l1
    currentl2 = l2
    count = 0
    previous = None
    new_head = None
    while currentl1 and currentl2:
        merge = ListNode()

        if currentl1.val <= currentl2.val:
            merge.val = currentl1.val
            currentl1 = currentl1.next
        else:
            merge.val = currentl2.val
            currentl2 = currentl2.next

        if previous:
            previous.next = merge

        previous = merge
        if count == 0:
            new_head = merge
        count += 1
    
    while currentl1:
        previous.next = currentl1
        previous = previous.next
        currentl1 = currentl1.next
        
    while currentl2:
        previous.next = currentl2
        previous = previous.next
        currentl2 = currentl2.next
    
    return new_head

head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(4)


head1 = ListNode(1)
head1.next = ListNode(3)
head1.next.next = ListNode(4)

new_head = merge_lists(head, head1)

itr = new_head
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")

def merge_lists1(l1, l2):
    dummy = ListNode(0)
    current = dummy

    while l1 and l2:
        if l1.val <= l2.val:
            current.next = l1
            l1 = l1.next
        else:
            current.next = l2
            l2 = l2.next
        current = current.next

    # attach remaining
    current.next = l1 if l1 else l2

    return dummy.next