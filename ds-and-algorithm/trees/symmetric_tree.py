class Node:
    def __init__(self, val=0, left = None, right = None):
        self.val = val
        self.left = left
        self.right = right

def symmetry(root):

    def compare(left, right):
        if left is None and right is None:
            return True
        if left is None or right is None:
            return False
        if left.val != right.val:
            return False
        left_tree = compare(left.left, right.right)
        right_tree = compare(left.right, right.left)
        return left_tree and right_tree

    return compare(root.left, root.right)



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

'''
Time:  O(n) — visits every node once
Space: O(h) — recursion depth
'''