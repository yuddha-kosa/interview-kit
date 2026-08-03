
class Node:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

def count_node(node):

    if node is None:
        return 0
    
    left_count = count_node(node.left)
    right_count = count_node(node.right)

    return 1 + left_count + right_count


root = Node(3)
root.left = Node(4)
root.right = Node(5)
root.left.left = Node(6)
root.left.right = Node(7)
root.right.left = Node(9)
root.right.right = Node(10)

print(count_node(root))