class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
def list_to_num(head):

    if not head:
        return
    
    current = head
    result = []

    while current:
        result.append(str(current.val))
        current = current.next
    
    res = "".join(result)
    return int(res)

head = ListNode(1)
head.next = ListNode(2)
head.next.next = ListNode(3)
head.next.next.next = ListNode(4)
head.next.next.next.next = ListNode(5)

print(list_to_num(head))

def list_to_num1(head):
    result = 0
    current = head

    while current:
        result = (result*10)+current.val
        current = current.next
    return result


print(list_to_num1(head))