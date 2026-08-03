
from collections import deque
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def right_side_view(root):

    que = deque([root])
    result = []
    while que:
        current = []
        for _ in range(len(que)):
            node = que.popleft()
            current.append(node.val)
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        result.append(current[-1])
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

print(right_side_view(root1))
print(right_side_view(root2))

'''
time: O(n)
space: O(l) + O(n/2) = O(n)
'''