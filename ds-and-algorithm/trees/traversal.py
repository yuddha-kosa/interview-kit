from collections import deque
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# DFS based
def inorder_traversal(root):
    output = []
    def inorder(node):
        if not node:
            return
        inorder(node.left)
        output.append(node.val)
        inorder(node.right)
    
    inorder(root)
    return output

# DFS based
def preorder_traversal(root):
    output = []
    def preorder(node):
        if node is None:
            return
        output.append(node.val)
        preorder(node.left)
        preorder(node.right)
    preorder(root)
    return output

# DFS based
def postorder_traversal(root):
    output = []
    def postorder(node):
        if node is None:
            return
        postorder(node.left)
        postorder(node.right)
        output.append(node.val)
    postorder(root)
    return output

# BFS based
def levelorder_traversal(root):
    if not root:
        return []
    
    que = deque([root])
    output = []
    while que:
        current = []
        '''
        que has n items at the START of an iteration → range(len(que))
        captures "n" BEFORE the loop starts appending new children.
        Even though que grows DURING the loop (as children get added),
        the for loop only runs n times — processing exactly the n
        nodes that existed at the start, not the newly-added ones.
        '''
        for _ in range(len(que)):
            node = que.popleft()
            current.append(node.val)

            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        output.append(current)
    return output


    

def build_tree(arr):
    if not arr or arr[0] is None:
        return None
    root = Node(arr[0])
    que = deque([root])
    i = 1
    while que and i < len(arr):
        node = que.popleft()
        if i < len(arr):
            if arr[i] is not None:
                node.left = Node(arr[i])
                que.append(node.left)
            i += 1
        if i < len(arr):
            if arr[i] is not None:
                node.right = Node(arr[i])
                que.append(node.right)
            i += 1
    return root

root = build_tree([1,2,3,4,5,None,8,None,None,6,7,9])

print("Inorder:", inorder_traversal(root))
print("Preorder:", preorder_traversal(root))
print("Postorder:", postorder_traversal(root))
print("Levelorder:", levelorder_traversal(root))