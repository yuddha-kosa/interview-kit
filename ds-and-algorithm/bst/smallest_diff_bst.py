
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

root1 = build_tree([5,3,8,2,4,7,10])
root2 = build_tree([10,5,15,None,None,12,20])

def smallest_difference(root):
    smallest = float('inf')
    prev = None
    def dfs(root):
        nonlocal prev
        nonlocal smallest
        if not root:
            return
        dfs(root.left)
        if prev:
            smallest = min(smallest, (root.val-prev.val))
        prev = root
        dfs(root.right)
    
    dfs(root)
    return smallest

print(smallest_difference(root1))
print(smallest_difference(root2))
'''
Time:  O(n) — visits every node once
Space: O(h) — recursion depth
'''