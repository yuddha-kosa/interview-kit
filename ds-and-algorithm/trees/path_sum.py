
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

root1 = build_tree([5,4,8,11,None,13,4,7,2,None,None,None,1])
root2 = build_tree([1,2,3])
root3 = build_tree([4,9,0,5,1])

def path_sum(root, target):
    def dfs(root, path):
        if root is None:
            return False
        if root.left is None and root.right is None:
            if root.val + path == target:
                return True
            return False
        path += root.val
        return dfs(root.left, path) or dfs(root.right, path)
    return dfs(root, 0)
    


print("Sum:",path_sum(root1, 22))
print("Sum:", path_sum(root2, 5))
print("Sum:", path_sum(root3, 6))


'''
time: O(n)
space: O(h)
'''