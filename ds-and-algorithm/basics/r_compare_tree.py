
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def compare_tree(node1, node2):
    def is_same(left, right):
        if left is None and right is None:
            return True
        if left is None or right is None:  
            return False
        if left.val != right.val:
            return False
        return is_same(left.left, right.left) and is_same(left.right, right.right)
    return is_same(node1, node2)

# Test Case
root = Node(1)
root.left = Node(2)
root.right = Node(3)
root.left.left = Node(4)
root.left.right = Node(5)
root.right.left = Node(6)
root.right.right = Node(7)

root2 = Node(1)
# level 1
root2.left = Node(2)
root2.right = Node(3)

# level 2
root2.left.left = Node(4)
root2.left.right = Node(5)
root2.right.left = Node(6)
root2.right.right = Node(7)


print(compare_tree(root, root2))