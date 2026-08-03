
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

root1 = build_tree([5,1,4,None,None,3,6])
root2 = build_tree([2,1,3])


def validate_BST(root):
    def is_valid(root, min_node, max_node):
        if root is None:
            return True
        if not (min_node < root.val < max_node):
            return False
        # a left child can not be greater than it's grand-parent even though it's on the right side of the left tree
        # and grand-parents value get's passed as the max value in the left sub-tree.
        left_tree = is_valid(root.left, min_node, root.val) 
        # a right child will always be greater than it's grand-parent even though it's on the left side of the right tree
        # and grand-parents value get's passed as the min value in the right sub-tree.
        right_tree = is_valid(root.right, root.val, max_node) 

        return left_tree and right_tree
    return is_valid(root, -float('inf'), float('inf'))

print(validate_BST(root1))
print(validate_BST(root2))



'''
                 20
              (-∞,+∞)
              /      \
             /        \
     (-∞,20)          (20,+∞)

        10               30
       /  \             /  \
(-∞,10) (10,20)   (20,30) (30,+∞)
'''