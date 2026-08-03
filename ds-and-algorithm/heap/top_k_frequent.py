import heapq

def top_k_frequent(nums,k):
    num_map = {}
    for num in nums:
        num_map[num] = num_map.get(num, 0) + 1
    
    min_heap = []

    for key, val in num_map.items():
        if len(min_heap) >= k and (val, key) > min_heap[0]:
            heapq.heappushpop(min_heap, (val, key))
        if len(min_heap) < k:
            heapq.heappush(min_heap, (val,key)) 
    result = []
    for m in min_heap: 
        f, n = m
        result.append(n)
        
    return result

print(top_k_frequent([4,4,4,6,6,7,7,7,7], 2))


'''
Time:  O(n) for building frequency map + O(n log k) for the
       heap operations = O(n log k)
Space: O(n) for frequency map + O(k) for heap = O(n)
'''