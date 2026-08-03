
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
root3 = build_tree([1,2,3])
root4 = build_tree([4,9,0,5,1])

def sum_root_to_leaf(root):

    results = []
    path = []

    def backtrack(node):
        if node is None:
            return
        path.append(str(node.val))
        if node.left is None and node.right is None:
            results.append(tuple(path[:]))
        backtrack(node.left)
        backtrack(node.right)
        path.pop()
    
    backtrack(root)
    print(f"results: {results}")
    sum_path = 0
    for result in results:
        sum_path += int("".join(result))

    return sum_path

def sum_root_to_leaf_v2(root):
    def dfs(node, current_number):
        if node is None:
            return 0
        current_number = current_number * 10 + node.val
        if node.left is None and node.right is None:
            return current_number
        return dfs(node.left, current_number) + dfs(node.right, current_number)
    return dfs(root, 0)


print("Sum:",sum_root_to_leaf(root1))
print("Sum:", sum_root_to_leaf(root2))
print("Sum:", sum_root_to_leaf(root3))
print("Sum:", sum_root_to_leaf(root4))


'''
time: O(n log n)
space: O(h)
'''