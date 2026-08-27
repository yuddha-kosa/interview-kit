def province_count(matrix):
    n = len(matrix)
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

        #print(f"before u, {u}, u_r: {u_r}, v: {v}, v_r: {v_r}") 
        if u_r == v_r:
            return
        #print(f"after u, {u}, u_r: {u_r}, v: {v}, v_r: {v_r}") 

        if rank[u_r] > rank[v_r]:
            parent[v_r] = u_r
            rootnum -= 1
        else:
            parent[u_r] = v_r
            if rank[u_r] == rank[v_r]:
                rank[v_r] += 1
                rootnum -= 1
                #print("total during2: ",rootnum)

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] != 0:
                #print(parent)
                union(i, j)

    print("Total province: ",rootnum)
    for k in range(len(parent)):
        p = find(k)
        root.add(p)
    return len(root)

print(province_count([[1,1,0], [1,1,0], [0,0,1]]))

'''
Time:  O(n² × α(n)) — n² for scanning the matrix, α(n) being
       the (nearly constant) cost of find/union with both
       optimizations
Space: O(n) — parent, rank, and root set
'''