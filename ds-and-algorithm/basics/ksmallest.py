import heapq

def k_smallest(nums, k):
    heap = []
    for num in nums:
        heapq.heappush(heap, -num)
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([-x for x in heap])


numb = [1,6,3,9,10,8,4]
k_numb = k_smallest(numb, 3)
print(f"k_numb:{k_numb}")