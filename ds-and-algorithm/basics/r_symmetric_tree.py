
class Node:
    def __init__(self, val):
        self.val = val
        #self.left = None
        #self.right = None
        self.left: "Node" | None = None
        self.right: "Node" | None = None

def symmetry(node):
    def is_mirror(nodeleft, noderight):
        # base case
        if nodeleft is None and noderight is None:
            return True
        if nodeleft is None and noderight is not None or noderight is None and nodeleft is not None:
            return False
        if nodeleft.val != noderight.val:
            return False

        return is_mirror(nodeleft.left, noderight.right) and is_mirror(nodeleft.right, noderight.left)
    return is_mirror(node.left, node.right)


'''
# Test Case
root = Node(1)
root.left = Node(2)
root.right = Node(2)
root.left.left = Node(3)
root.left.right = Node(4)
root.right.left = Node(4)
root.right.right = Node(3)
#root.right.right = Node(4)
print(symmetry(root))  # Output: 3

'''
root = Node(1)
# level 1
root.left = Node(2)
root.right = Node(2)

# level 2
root.left.left = Node(3)
root.left.right = Node(4)
root.right.left = Node(4)
root.right.right = Node(3)

# level 3
root.left.left.left = Node(5)
root.left.left.right = Node(6)
root.left.right.left = Node(7)
root.left.right.right = Node(8)
root.right.left.left = Node(8)
root.right.left.right = Node(7)
root.right.right.left = Node(6)
root.right.right.right = Node(5)

print(symmetry(root))