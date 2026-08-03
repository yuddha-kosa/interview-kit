from collections import deque
class Node:
    def __init__(self, val = 0, left = None, right = None):
        self.left = left
        self.right = right
        self.val = val

class Operations:
    def __init__(self, root_val):
        self.root = Node(root_val)
    def insert(self, val):
        if self.root == None:
            self.root = Node(val)
            return

        que = deque([self.root])

        while que:
            node = que.popleft()
            if node.left == None:
                node.left = Node(val)
                return
            if node.right == None:
                node.right = Node(val)
                return
            que.append(node.left)
            que.append(node.right)
    
    def search(self, target):
        if not self.root:
            return False

        que = deque([self.root])

        while que:
            node = que.popleft()
            if node.val == target:
                return True
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        return False
    
    def delete(self, target):
        # first find the target node
        # find the deepest right node
        # replace target with the deepest node
        # delete the depest node by seeting it's parent to None
        if not self.root:
            return False
        t_node = None
        que = deque([self.root]) 

        while que:
            node = que.popleft()
            if node.val == target:
                t_node = node
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        if not t_node:
            return
        # find deepest and replace
        d_node = self.deepest_node()

        if self.root == d_node:
            self.root = None
            return

        t_node.val = d_node.val

        # delete the deepest node
        pa_dep = deque([self.root])
        while pa_dep:
            node = pa_dep.popleft()
            if node.left:
                dl_node = node.left
                #if dl_node.val == d_node.val: #wrong
                if dl_node == d_node:
                    node.left = None
                    return
                else:
                    pa_dep.append(node.left)
            if node.right:
                dr_node = node.right
                #if dr_node.val == d_node.val: #wrong
                if dr_node == d_node:
                    node.right = None
                    return
                else:
                    pa_dep.append(node.right)

    def deepest_node(self):
        node = None
        que = deque([self.root]) 

        while que:
            node = que.popleft()
            if node.left:
                que.append(node.left)
            if node.right:
                que.append(node.right)
        
        return node

