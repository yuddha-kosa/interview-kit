import heapq

# smallest at the root in min heap and largest at root in max heap.
heap = []

heapq.heappush(heap, 10)
heapq.heappush(heap, 1)
heapq.heappush(heap, 2)
heapq.heappush(heap, 4)
heapq.heappush(heap, 3)
heapq.heappush(heap, 7)

print(f"heap: {heap}")
print(f"heap[:3]: {heap[:3]}")

pop_small = heapq.heappop(heap)
print(f"pop_element: {pop_small}")
print(f"heap: {heap}")

num = [2,3,1,4,5]

heapq.heapify(num)
num2 = [8,9,10]
heapq.heapify(num2)
print(f"num: {num}")

pop_small1 = heapq.heappop(num)
print(f"pop_element2: {pop_small1}")


heapt = []

# Push (priority, value) tuples
heapq.heappush(heapt, (3, "task C"))
heapq.heappush(heapt, (1, "task A"))
heapq.heappush(heapt, (2, "task B"))

priority, task = heapq.heappop(heapt)
print(f"priority: {priority}, task: {task}")