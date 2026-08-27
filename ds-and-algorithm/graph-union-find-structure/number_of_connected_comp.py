def number_of_connected_comp(n, edges):
    parent = list(range(n))
    rank = [0]*n

    root = set()
    rootnum = n

    #print("total: ",rootnum)
    def find(x):
        if parent[x] == x:
            return x
        parent[x] = find(parent[x])
        return parent[x]
    
    def union(u, v):
        nonlocal rootnum
        u_r = find(u)
        v_r = find(v)

        if u_r == v_r:
            return

        if rank[u_r] > rank[v_r]:
            parent[v_r] = u_r
            rootnum -= 1
        else:
            parent[u_r] = v_r
            rootnum -= 1
            if rank[u_r] == rank[v_r]:
                rank[v_r] += 1


    for src, dst in edges:
        union(src, dst)
    
    print("rootnum: ", rootnum)
    for k in range(len(parent)):
        p = find(k)
        root.add(p)
    return len(root)

print(number_of_connected_comp(3, [[0,1], [0,2]]))
print(number_of_connected_comp(6, [[0,1], [1,2], [2,3], [4,5]]))

'''
time: O(e alpha n)
space: O(n)
'''