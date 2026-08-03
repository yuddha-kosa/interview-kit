#1. list — your Go slice
nums = [3,1,4,1,5]
nums.append(6)       # O(1)
nums.pop()           # O(1) — removes last
nums.pop(0)          # O(n) — avoid in hot loops
nums.sort()          # O(n log n) in place
sorted(nums)         # returns new sorted list
nums[::-1]           # reverse — very Pythonic
#2. dict — your Go map (use this constantly)
freq = {}
freq["a"] = freq.get("a", 0) + 1  # count pattern

# Even cleaner with defaultdict
from collections import defaultdict
freq = defaultdict(int)
freq["a"] += 1        # no KeyError ever

#3. set — O(1) lookup, no duplicates
seen = set()
seen.add(5)
5 in seen            # O(1) — use this over list for lookups
seen.remove(5)       # KeyError if missing
seen.discard(5)      # safe remove
#4. deque — your queue/stack (import this, not list)
from collections import deque
q = deque()
q.append(1)          # enqueue right — O(1)
q.appendleft(1)      # enqueue left — O(1)
q.pop()              # dequeue right — O(1)
q.popleft()          # dequeue left — O(1)
# Use for BFS always. list.pop(0) is O(n) — never use it
#5. heapq — min-heap (used in Dijkstra, top-K problems)
import heapq
heap = []
heapq.heappush(heap, 3)
heapq.heappush(heap, 1)
heapq.heappop(heap)  # returns 1 (smallest)

# Max-heap trick: negate values
heapq.heappush(heap, -val)
max_val = -heapq.heappop(heap)

#6. Tuple — lightweight, immutable pair
point = (3, 4)
x, y = point          # unpacking — use this everywhere
pairs = [(1,'a'), (2,'b')]
pairs.sort()           # sorts by first element auto

#Python tricks that make DSA solutions cleaner
# Swap without temp variable (Go needs temp)
a, b = b, a

# Infinity (for min/max problems)
float('inf')    # use instead of math.MaxInt
float('-inf')

# Integer division (like Go's /)
7 // 2          # = 3, not 3.5

# Modulo — same as Go
7 % 3           # = 1

# Power
2 ** 10         # = 1024

# List comprehension — replaces many for loops
squares = [x*x for x in range(10)]
evens   = [x for x in nums if x % 2 == 0]

# Check if string is digit/alpha
"123".isdigit()
"abc".isalpha()

# String to list and back
chars = list("hello")
"".join(chars)