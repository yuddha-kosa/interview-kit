class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Operations:
    def __init__(self, root_val):
        self.root = Node(root_val)

    def insert(self, root, val):
        if not root:
            return Node(val)
        
        if val < root.val:
            root.left = self.insert(root.left, val)
        else:
            root.right = self.insert(root.right, val)
        return root
    def delete(self, root, target):
        if root is None:
            return None
        if target < root.val:
            root.left = self.delete(root.left, target)
        elif target > root.val:
            root.right = self.delete(root.right, target)
        else:
            # check if node has one or zero element then just return the remaining one or zero elemet
            # and the caller method will attach the returned element.
            if root.left is None:
                return root.right
            elif root.right is None:
                return root.left
            
            # if node has 2 elements and if we have to delete it then there are two options:
            # 1. from the left subtree get the largest element and replace it with the element to delete
            # 2 or from the right subtree and get the smallest element and replace it with the element to
            # delete. The idea is to maintain the BST property.
            temp = self.min_right_node(root.right)
            root.val = temp.val
            root.right = self.delete(root.right, temp.val)
            return root

    def min_right_node(self, root):
        while root.left is not None:
            root = root.left
        return root
            
    def max_left_node(self, root):
        while root.right is  not None:
            root = root.right
        return root

    def search(self, root, key):
        while root:
            if key < root.val:
                root = root.left
            elif key > root.val:
                root = root.right
            else:
                return True

        return False








def build_bst(arr,start, end):
    if start > end:
        return None
    mid = (start + end)//2
    node = Node(arr[mid])
    node.left = build_bst(arr, start, mid-1)
    node.right = build_bst(arr, mid+1, end)
    
    return node


def to_bst(arr):
    return build_bst(arr, 0, len(arr)-1)


node= to_bst([1,2,3,4,5,6,7])

print(f"root: {node.val}")
def in_order(node):
    def dfs(node):
        if node == None:
            return
        dfs(node.left)
        print(node.val)
        dfs(node.right)

    dfs(node)
in_order(node)

op = Operations(node)
new_node = op.insert(node, 8)
print(f"root after insert: {new_node.val}")
in_order(new_node)


'''
Plain tree search:  no ordering info → must check ALL nodes
                    at every level → total = n

BST search:         ordering info → check ONLY 1 node per
                    level (know which way to go) → total = h
                                                            = log n
'''