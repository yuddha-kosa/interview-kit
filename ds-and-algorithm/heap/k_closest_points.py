import heapq
import math
def k_closest_points(arr, k):
    min_heap = []
    for point in (arr):
        p1 = point[0]
        p2 = point[1]
        sq = (p1*p1) + (p2*p2)
        dist = -math.sqrt(sq)
        if len(min_heap) < k:
            heapq.heappush(min_heap, (dist,[p1, p2]))
        else:
            if (dist,[p1, p2]) > min_heap[0]:
                heapq.heappushpop(min_heap, (dist, [p1, p2]))
    
    result = []
    for m in min_heap:
        _, pt = m
        result.append(pt)
    return result




print(k_closest_points([[4,4], [1,2], [2,3]], 2))
print(k_closest_points([[-1,-1], [2,2], [0,1], [1, -1]], 3))

'''
time: O(n log k)
space: O(k)
'''