
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

def max_tree_depth(root):

    if not root:
        return 0
    left_height = max_tree_depth(root.left)
    right_height = max_tree_depth(root.right)

    return 1 + max(left_height, right_height)




print(max_tree_depth(root1))
print(max_tree_depth(root2))


'''
time: O(n)
space: O(h)
'''