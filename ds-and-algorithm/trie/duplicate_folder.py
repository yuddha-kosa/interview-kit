from collections import defaultdict

class TriNode:
    def __init__(self):
        self.children = {}
        self.delete = False
        self.serial = ""

class Operation:
    def __init__(self):
        self.root = TriNode()
    
    def insert(self, arr):
        node = self.root

        for ch in arr:
            if ch not in node.children:
                node.children[ch] = TriNode()
            node = node.children[ch]
    
    def get_root(self):
        return self.root

def duplicate_folder(arr):

    # create trie and insert all the dir
    # every subfolder is a node in the trie.
    op = Operation()
    for dir in arr:
        op.insert(dir)
    
    #root = op.get_root()
    serialize_count = defaultdict(int)
    def serialize(node):
        if len(node.children) == 0:
            #node.serial = "()" This will remove all the leaf nodes
            #serialize_count[node.serial] += 1
            #return node.serial
            return ""
        children = []
        #for name, child in node.children.items():
        for name in sorted(node.children):
            child = node.children[name]
            se = "("+name+serialize(child)+")"
            children.append(se)
        
        node.serial = "".join(children)
        serialize_count[node.serial] += 1
        return node.serial

    serialize(op.root)
    print(f"serial_count: {serialize_count}")
    def mark(node):
        if node is not op.root and serialize_count[node.serial] > 1:
            node.delete = True
            return
        for _, child in node.children.items():
            mark(child)
    mark(op.root)

    results = []
    def dfs(node, path):

        for name, child in node.children.items():
            if child.delete == True:
                continue
            path.append(name)
            results.append(path[:])
            dfs(child, path)
            path.pop()
    dfs(op.root, [])
    return results 

print(duplicate_folder([["a"],["c"],["d"],["a","b"],["c","b"],["d","a"]]))
print(duplicate_folder([["a"],["c"],["a","b"],["c","b"],["a","b","x"],["a","b","x","y"],["w"],["w","y"]]))

'''
    dir = {}
    def find_duplicate(node, val):
        if len(node.children) == 0:
            dir[""].append(val)
            return ""
        
        for ch in node.children:
            g_child = find_duplicate(node.children[ch], ch)
            if g_child:
                child = ch + g_child 
            else:
                child = ch
            dir[child].append(val)
    
        return child
    find_duplicate(root, "")
    print(f"dir: {dir}")

    def del_child(node, word):
        if len(node.children) == 0:
            return
        for ch in node.children:
            g_child = del_child(node.children[ch], ch)
            if g_child:
                child = ch + g_child 
            else:
                child = ch
            if child == word:
                del(node.children[ch])
        return
    for sub_folder, nodes in dir.items():
        if len(nodes) > 1:
            for folder in nodes:
                del_child(root, folder+sub_folder)
    
    results = []
    def dfs(node, curr):
        if node is None:
            curr = []
            return
        for ch in node.children:
            curr.append(ch)
            results.append(curr)
            dfs(node.children[ch], curr)
    
    dfs(root, [])

    return results
'''