class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def height_of_tree(tn):
    
    if tn == None:
        return -1
    
    l_max = height_of_tree(tn.left)
    r_max = height_of_tree(tn.right)

    return 1 + max(l_max, r_max)



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

print(height_of_tree(tn))