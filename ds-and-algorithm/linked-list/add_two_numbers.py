class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def add_numbers(l1, l2):

    if not l1 and not l2:
        return
    
    list1 = l1
    list2 = l2
    carry = 0
    previous = None
    head = None
    while list1 and list2:
        val1 = list1.val
        val2 = list2.val
        sum = val1 + val2 + carry

        carry = sum//10
        num = sum%10
        node = ListNode(num)
        if previous:
            previous.next = node    
        else:
            head = node
        previous = node
        list1 = list1.next
        list2 = list2.next
    while list1:
        val1 = list1.val
        sum = val1 + carry
        carry = sum//10
        num = sum%10
        new_node = ListNode(num)
        node.next = new_node
        node = node.next
        list1 = list1.next

    while list2:
        val2 = list2.val
        sum = val2 + carry
        carry = sum//10
        num = sum%10
        new_node = ListNode(num)
        node.next = new_node
        node = node.next
        list2 = list2.next

    if carry != 0:
        new_node = ListNode(carry)
        node.next = new_node

    return head

'''
head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(4)


head1 = ListNode(1)
head1.next = ListNode(9)
head1.next.next = ListNode(5)

new_head = add_numbers(head, head1)
itr = new_head
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")
'''

def add_numbers1(l1, l2):
    dummy = ListNode(0)
    current = dummy
    carry = 0

    while l1 or l2 or carry:
        if l1:
            val1 = l1.val
            l1 = l1.next
        else:
            val1 = 0
        if l2:
            val2 = l2.val
            l2 = l2.next
        else:
            val2 = 0

        total = val1 + val2 + carry
        carry = total // 10
        new_node = ListNode(total % 10)
        current.next = new_node
        
        current = current.next

    return dummy.next


head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(4)


head1 = ListNode(1)
head1.next = ListNode(9)
head1.next.next = ListNode(5)

new_head = add_numbers1(head, head1)
itr = new_head
while itr:
    print(itr.val, end=" → ")
    itr = itr.next
print("\n")