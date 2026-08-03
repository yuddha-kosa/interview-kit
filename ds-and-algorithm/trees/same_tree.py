class Node:
    def __init__(self, val=0, left = None, right = None):
        self.val = val
        self.left = left
        self.right = right

def same_tree(tree1, tree2):

    if tree1 is None and tree2 is None:
        return True
    if tree1 is None or tree2 is None:
        return False
    if tree1.val != tree2.val:
        return False

    left_tree_comp = same_tree(tree1.left, tree2.left)
    right_tree_comp = same_tree(tree1.right, tree2.right)
    return left_tree_comp and right_tree_comp


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


print(same_tree(root, root2))

'''
Time:  O(min(n1, n2)) — stops early on first mismatch
Space: O(min(h1, h2)) — recursion depth
'''