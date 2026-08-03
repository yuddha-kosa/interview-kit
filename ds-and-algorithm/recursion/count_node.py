class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def count_nodes(root):
    if root == None:
        return 0
    
    l_count = count_nodes(root.left)
    r_count = count_nodes(root.right)

    return 1 + l_count + r_count
    



tn = TreeNode(6)
tn.left = TreeNode(4)
tn.left.left = TreeNode(2)
tn.left.right = TreeNode(5)
tn.left.left.left = TreeNode(1)
tn.left.left.right = TreeNode(3)


tn.right = TreeNode(9)
tn.right.right = TreeNode(10)
tn.right.left = TreeNode(7)
tn.right.right.right = TreeNode(11)
tn.right.right.left = TreeNode(8)

print(count_nodes(tn))