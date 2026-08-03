'''
# Build this tree:
#         1
#        / \
#       2   3
#      / \
#     4   5

'''
class Node:
    def __init__(self, val):
        self.val = val
        #self.left = None
        #self.right = None
        self.left: "Node" | None = None
        self.right: "Node" | None = None

def height_of_tree(node):

    # base case
    if node is None:
        return 0
    
    # one call
    left = height_of_tree(node.left)
    right = height_of_tree(node.right) 

    height = 1 + max(left, right)
    return height

# Test Case
root = Node(1)
root.left = Node(2)
root.right = Node(3)
root.left.left = Node(4)
root.left.right = Node(5)

print(height_of_tree(root))  # Output: 3