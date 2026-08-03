
from collections import deque
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def zigzag_order(root):

    que = deque([root])
    result = []
    count = 1
    while que:
        current = deque()
        for _ in range(len(que)):
            node = que.popleft()
            if count % 2 == 0:
                current.appendleft(node.val)
            else:
                current.append(node.val)
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        result.append(list(current))
        count += 1
    return result

def zigzag_order1(root):
    if not root:
        return []
    que = deque([root])
    result = []
    left_to_right = True
    while que:
        current = []
        for _ in range(len(que)):
            node = que.popleft()
            current.append(node.val)
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        if not left_to_right:
            current.reverse()
        result.append(current)
        left_to_right = not left_to_right
    return result



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

root1 = build_tree([1,2,3,4,5,None,8,None,None,6,7,9])
root2 = build_tree([1,2,3,4,None,None,None,5])

print(zigzag_order(root1))
print(zigzag_order(root2))

'''
time: O(n)
space: O(n)
'''