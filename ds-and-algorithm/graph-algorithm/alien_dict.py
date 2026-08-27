from collections import deque
def alien_order(words):

    graph = {}
    indegree = {}
    for word in words:
        for ch in word:
            graph[ch] = graph.get(ch, [])
            indegree[ch] = indegree.get(ch, 0)

    for i in range(len(words)-1):
        word1 = words[i]
        word2 = words[i+1]

        if len(word1) > len(word2) and word1[:len(word2)] == word2:
            return False
        for k in range(len(word1)):
            #if k > len(word2)-1:
            #    break 
            if word1[k] == word2[k]:
                continue
            elif word1[k] != word2[k]:
                if word2[k] not in graph[word1[k]]: 
                    graph[word1[k]].append(word2[k]) 
                    indegree[word2[k]] = indegree.get(word2[k], 0) + 1
                #graph[word1[k]].append(word2[k]) 
                #indegree[word1[k]] = indegree.get(word1[k], 0)
                #indegree[word2[k]] = indegree.get(word2[k], 0) + 1
                break
    queue = deque()

    for vertx, degree in indegree.items():
        if degree == 0:
            queue.append(vertx)
    result = []
    while queue:
        node = queue.popleft()
        result.append(node)
        if node not in graph:
            continue
        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)

    print(result) 
    if len(result) == len(indegree):
        return True
    return False


words = ["wrt", "wrf", "er", "ett", "rftt"]
print(alien_order(words)) 

words = ["bat",  "cat", "cab"]
print(alien_order(words)) 

words = ["qwert", "qwerz", "qwx", "qwxy"]
print(alien_order(words)) 


'''
Total Time = O(N×L) + O(N×L) + O(V+E)
           = O(N×L)     [since V+E is typically SMALLER —
                          V is bounded by a small alphabet,
                          E ≤ N-1, both dominated by N×L for
                          any words longer than 1 character]

graph, indegree: O(V) — bounded by alphabet size
queue, result:   O(V) — same bound
(the words themselves): O(N×L) — if counting input storage

Total: O(V) auxiliary + O(N×L) if counting input                          
'''