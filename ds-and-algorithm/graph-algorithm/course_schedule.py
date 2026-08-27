from collections import deque

def can_finish(num_courses, prerequisites):
    graph = {}
    indegree = [0]*num_courses
    for dest, src in prerequisites: # prerequisites[i] = [a, b]   (course a requires course b first)
        if src not in graph:
            graph[src] = []
        graph[src].append(dest)
        indegree[dest] += 1

    queue = deque()

    for i in range(num_courses):
        if indegree[i] == 0:
            queue.append(i) 
    result = []    
    while queue:
        node = queue.popleft()
        result.append(node)
        #print(f"node: {node}, result: {result}")
        if node not in graph:
            continue
        for neighbour in graph[node]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour) 
    
    if len(result) != num_courses:
        return False
    print(result)
    return True



prerequisites = [[2,1], [1,0]]
num_courses = 3
print(can_finish(num_courses, prerequisites))

prerequisites = [[1,0], [0,2], [2,1]]
print(can_finish(num_courses, prerequisites))

'''
Time:  O(V+E)
Space: O(V+E)
'''