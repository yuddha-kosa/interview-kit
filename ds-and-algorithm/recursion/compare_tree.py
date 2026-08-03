class Node:
    def __init__(self, val=0, left = None, right = None):
        self.val = val
        self.left = left
        self.right = right
'''
def compare_tree(node11, node22):
    def is_same(node1, node2):
        if node1 == None and node2 == None:
            return True
        if node1 == None or node2 == None:
            return False 
        if node1.val != node2.val:
            return False
        left_tree = is_same(node1.left, node2.left)
        right_tree = is_same(node1.right, node2.right)
        return left_tree and right_tree
    return is_same(node11, node22)
'''
    
def compare_tree(node1, node2):
    if node1 == None and node2 == None:
        return True
    if node1 == None or node2 == None:
        return False 
    if node1.val != node2.val:
        return False
    left_tree = compare_tree(node1.left, node2.left)
    right_tree = compare_tree(node1.right, node2.right)
    return left_tree and right_tree

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
root2.left = Node(20)
root2.right = Node(3)

# level 2
root2.left.left = Node(4)
root2.left.right = Node(5)
root2.right.left = Node(6)
root2.right.right = Node(7)


print(compare_tree(root, root2))