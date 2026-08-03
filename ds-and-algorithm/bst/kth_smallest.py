
from collections import deque
class Node:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

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

root1 = build_tree([3,1,4,None,2])
root2 = build_tree([5,3,6,2,4,None,None,1])



def kth_smallest(root, k):
    visit_count = 0
    kth_val = 0
    found = False
    def dfs(root):
        nonlocal visit_count
        nonlocal kth_val
        nonlocal found

        if not root or found:
            return
        
        dfs(root.left)
        if found:
            return
        visit_count += 1
        if visit_count == k:
            found = True
            kth_val = root.val
            return
        dfs(root.right)
    dfs(root)
    return kth_val

print(kth_smallest(root1, 1))
print(kth_smallest(root2, 3))


'''
Time O(h + k)
Space: O(h)


BST search (for a SPECIFIC target value):
    You KNOW which direction to go at EVERY step (left or
    right), because you're comparing against ONE target value.
    This means you NEVER backtrack — you go DOWN, and DOWN
    only, until you either find the target or hit None.

    Maximum work = height of the tree = O(h) = O(log n)
    (for a balanced tree)


kth_smallest (finding the kth element in SORTED ORDER):
    There's no single "target value" to compare against —
    you need to count UP TO the kth position in sorted order.
    This requires potentially GOING DOWN to find the smallest,
    then BACKTRACKING UP, then possibly going DOWN AGAIN into
    a right subtree, repeating this pattern k times.

    This is NOT bounded by height ALONE — it depends on BOTH
    the height (to reach the starting point) AND k (how many
    "next" steps are needed after that).

    Total work = O(h + k), NOT just O(h)

BST search:      "find ONE specific value" → single downward
                 path → bounded by h alone

kth_smallest:    "count through k values in order" → requires
                 REVISITING the tree structure repeatedly
                 (down, up, down again) → bounded by h (getting
                 started) PLUS k (the counting itself)
'''