
import heapq
def kth_largest(nums,k):

    neg_arr = [-i for i in nums]
    heapq.heapify(neg_arr)
    kth_element = None
    for i in range(k):
        kth_element = heapq.heappop(neg_arr)
    return -kth_element

print(kth_largest([7,10,4,3,20,15], 3))

'''
time: O(n + klog n)
space: O(n)
'''  

def kth_largest_2(nums, k):

    min_heap = []

    for i in range(k):
        heapq.heappush(min_heap, nums[i])
    
    for i in range(k, len(nums)):
        if nums[i] > min_heap[0]:
            heapq.heappushpop(min_heap, nums[i])
    
    return min_heap[0]

print(kth_largest([7,10,4,3,20,15], 3))
'''
time: O(n log k)
space: O(k)
'''  


