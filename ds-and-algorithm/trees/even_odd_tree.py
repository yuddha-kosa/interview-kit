
from collections import deque
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(arr):
    if not arr or arr[0] is None:
        return None
    root = Node(arr[0])
    que = deque([root])
    i = 1
    while que and i < len(arr):
        node = que.popleft()
        if i < len(arr):
            if arr[i] is not None:
                node.left = Node(arr[i])
                que.append(node.left)
            i += 1
        if i < len(arr):
            if arr[i] is not None:
                node.right = Node(arr[i])
                que.append(node.right)
            i += 1
    return root

root1 = build_tree([1,10,4,3,None,7,9,12,8,6,None,None,2])
root2 = build_tree([5,4,2,3,3,7])

def is_even_odd_tree(root):

    que = deque([root])
    count = 0
    while que:
        last_odd = -float('inf') 
        last_even = float('inf')

        for _ in range(len(que)):
            node = que.popleft()
            #print(f"level: {count}, que: {node.val}")
            # if count/level is even, then number should be odd and increasing order.
            if count % 2 == 0:
                if node.val % 2 == 0:
                    return False
                if node.val <= last_odd:
                    return False
                last_odd = node.val

            # if count/level is odd, then number should be even and decreasing order.
            else:
                if node.val % 2 != 0:
                    return False
                if node.val >= last_even:
                    return False
                last_even = node.val
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        count += 1
    return True



print(is_even_odd_tree(root1))
print(is_even_odd_tree(root2))


'''
time: O(n)
space: O(n)
'''