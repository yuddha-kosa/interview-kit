
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

#root1 = build_tree([1,10,4,3,None,7,9,12,8,6,None,None,2])
#root2 = build_tree([5,4,2,3,3,7])
root1 = build_tree([3,4,5,1,2])
root2 = build_tree([4,1,2])
root3 = build_tree([3,4,5,1,2,None,None,None,None,0])


def same_tree(tree1, tree2):

    if tree1 is None and tree2 is None:
        return True
    
    if tree1 is None or tree2 is None:
        return False
    if tree1.val != tree2.val:
        return False
    left_tree = same_tree(tree1.left, tree2.left)
    right_tree = same_tree(tree1.right, tree2.right)

    return left_tree and right_tree

def sub_tree(tree1, tree2):
    matching_nodes = []
    def dfs(node):
        if node is None:
            return
        if node.val == tree2.val:
            matching_nodes.append(node)
        dfs(node.left)
        dfs(node.right)
    
    dfs(tree1)
    matched = False
    for root in matching_nodes:
        matched = same_tree(root, tree2)
        if matched:
            return True 
    return matched


def sub_tree1(tree1, tree2):
    def dfs(node):
        if node is None:
            return False
        if node.val == tree2.val and same_tree(node, tree2):
            return True
        return dfs(node.left) or dfs(node.right)
    return dfs(tree1)



print(sub_tree(root1, root2))
print(sub_tree(root3, root2))


'''
time: O(m*n)
space: O(max(h1, h2))
'''