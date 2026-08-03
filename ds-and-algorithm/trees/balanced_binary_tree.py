
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
root3 = build_tree([3,9,20,None,None,15,7])
root4 = build_tree([1,2,2,3,3,None,None,4,4])

def balanced_binary_tree(root):
    balanced = True
    def height(root):
        nonlocal balanced
        if root is None:
            return 0
        left_height = height(root.left)
        right_height = height(root.right)

        diff = left_height-right_height
        if diff > 1 or diff < -1:
            balanced = False
        return 1 + max(left_height, right_height)
    h = height(root)
    return balanced



print("Balanced:", balanced_binary_tree(root1))
print("Balanced:", balanced_binary_tree(root2))
print("Balanced:", balanced_binary_tree(root3))
print("Balanced:", balanced_binary_tree(root4))

def is_balanced(root):
    def height(node):
        if node is None:
            return 0
        left = height(node.left)
        if left == -1:
            return -1          # already imbalanced somewhere below, propagate up immediately
        right = height(node.right)
        if right == -1:
            return -1          # same here
        if abs(left - right) > 1:
            return -1          # found imbalance AT this node
        return 1 + max(left, right)
    return height(root) != -1
'''
time: O(n)
space: O(h)
'''