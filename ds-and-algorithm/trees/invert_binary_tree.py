
from collections import deque
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# BFS based
def levelorder_traversal(root):
    if not root:
        return []
    
    que = deque([root])
    output = []
    while que:
        current = []
        for _ in range(len(que)):
            node = que.popleft()
            current.append(node.val)

            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        output.append(current)
    return output

def invert_tree(root):
    if root is None:
        return
    root.left, root.right = root.right, root.left
    invert_tree(root.left)
    invert_tree(root.right)

def invert_tree1(root):
    if root is None:
        return None
    left = invert_tree(root.left)      # fully invert left subtree first
    right = invert_tree(root.right)    # fully invert right subtree first
    root.left, root.right = right, left  # THEN swap at this level
    return root

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

print(levelorder_traversal(root1))
print(levelorder_traversal(root2))

print(invert_tree(root1))
print(invert_tree(root2))


print(levelorder_traversal(root1))
print(levelorder_traversal(root2))
'''
time: O(n)
space: O(h)
'''