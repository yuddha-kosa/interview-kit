class Node:
    def __init__(self, val=0, left = None, right = None):
        self.val = val
        self.left = left
        self.right = right
def symmetry(node):
    
    def is_symmetric(nleft, nright):
       if nleft == None and nright == None:
           return True
       if nleft == None or nright == None:
           return False
       if nleft.val != nright.val:
           return False
        
       l_sym = is_symmetric(nleft.left, nright.right)
       r_sym = is_symmetric(nleft.right, nright.left)
       return l_sym and r_sym

    return is_symmetric(node.left, node.right)

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