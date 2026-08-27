'''
class Node:
    children = [Node1, Node2]
    is_leaf = False
    title = ""
    url = ""


class TreeNode:
    __init__(self):
        self.children = {} # children[children] = TreeNode()
        is_leaf = False
        title = ""
        url = ""

node = Tree()
node.title = "level1"
node.children["level10"] = Tree()
node.children["level11"] = Tree()
node.children["level12"] = Tree()

level1 = node.children
level1.title = "level2"
level1.children[level20] = tree()
level1.children[level21] = tree()

level2 = level1.children
for ch in level2:
    if ch.is_leaf:
        ch.title = "title"
        ch.url = "url"





two approaches to check for duplicate
1. use a set to keep all the duplicate
2. use hash map.
duplicate: {
    url1: {node1:key, node2:key, node3:key}
    url2: {node10, node12, node13}
}
'''
'''
**Delete Duplicate Bookmarks**

---

**Problem Statement:**

```
You are given a browser's bookmark structure. Bookmarks are
organized into FOLDERS, which can be NESTED arbitrarily deep
(a folder can contain sub-folders, which can contain further
sub-folders, and so on). Each LEAF of this hierarchy is either
a bookmark (with a NAME and a URL) or an empty folder.

Two bookmarks are considered DUPLICATES if they point to the
SAME URL, regardless of their name, their folder location, or
how deep they are nested.

Write a function that removes all DUPLICATE bookmarks from
the structure, keeping only the FIRST occurrence encountered
(by any consistent traversal order). After removing a
duplicate bookmark, if a folder becomes EMPTY as a result
(no bookmarks and no sub-folders remaining), that empty
folder should ALSO be removed — and this should cascade
upward (removing newly-empty parent folders too).
```

---

**Example:**

```
Input:
    /level1/level2/level3/  →  {"test": "www.test.com"}
    /level10/level20/level30/  →  {"test": "www.test.com"}

Both bookmarks point to the SAME url ("www.test.com"),
despite different names/paths.

Output (after dedup):
    /level1/level2/level3/  →  {"test": "www.test.com"}

    (the second bookmark is removed, and since level30,
     level20, level10 become empty as a result, they are
     ALL removed too)
```

---

**Constraints / things to think about:**

```
- Folder structure can be arbitrarily deep
- Multiple bookmarks can exist within the SAME folder
- The SAME URL could appear at ANY depth, in ANY folder
- Removing a bookmark may cascade into removing empty
  ancestor folders
```

---

**Suggested approach:** build the folder hierarchy as a tree (similar to a Trie),
then do a POST-ORDER DFS — process children FIRST, track seen URLs in a shared map,
remove duplicate bookmarks, and let each level decide whether IT should also be
removed (based on whether its own children/bookmarks are now empty) — same pattern as
your Trie `delete()` function.

---

'''
class TreeNode:
    def __init__(self):
        self.children = {}
        self.is_leaf = False
        self.name_url = {}

class Operations:
    def __init__(self, root_key):
        node = TreeNode()
        node.children[root_key] = TreeNode()
        self.root = node
    def insert(self, input):
        node = self.root
        for dir, details in input.items():
            if not details["is_leaf"]:
                if dir not in node.children:
                    node.children[dir] = TreeNode()
                node = node.children[dir]
            else:
                if dir not in node.children:
                    node.children[dir] = TreeNode()
                    node.children[dir].is_leaf = True
                    for name, url in details["name_url"].items():
                        node.children[dir].name_url[name] = url

    def book_mark_remove_duplicate(self):
        duplicate = {}
        node = self.root
        def dfs(node, duplicate):
            to_delete = []    

            for dir, node_child in node.children.items():
                if node_child.is_leaf:
                    for name in list(node_child.name_url.keys()):
                        url = node_child.name_url[name]
                        if url in duplicate:
                            del(node_child.name_url[name])
                        else:
                            duplicate[url] = name
                    if len(node_child.name_url) == 0:
                        to_delete.append(dir) 
                dfs(node_child, duplicate)
        
            for dir in to_delete:
                del node.children[dir]

        dfs(node, duplicate)
    def travere(self):
        node = self.root
        result = []
        def dfs(node):

            for dir, node_child in node.children.items():
                result.append(dir)
                if node_child.is_leaf:
                    for name, url in node_child.name_url.items():
                        result.append((name,url))
                dfs(node_child)
        dfs(node)
        return result



input1 = {"level1": {"is_leaf": False}, "level2": {"is_leaf": False}, "level3": {"is_leaf": True, "name_url": {"test": "www.test.com"}}}
input2 = {"level10": {"is_leaf": False}, "level20": {"is_leaf": False}, "level30": {"is_leaf": True, "name_url": {"test": "www.test.com"}}}
op = Operations("bookmark")
op.insert(input1)
op.insert(input2)

print("Traversal before remving the duplicate:", op.travere())

op.book_mark_remove_duplicate()

print("Traversal after remving the duplicate:", op.travere())
