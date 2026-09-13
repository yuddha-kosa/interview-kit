**Pattern 1 — Exact match search:**
```
while left <= right; mid=(left+right)//2
if match: return mid; else left=mid+1 or right=mid-1 (discard mid entirely)

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

**Pattern 2 — FIRST position satisfying condition:**
```
while left < right; right starts at len(arr); mid=(left+right)//2
if condition True: right=mid (keep mid, search left); else left=mid+1 (discard mid)

def find_first_true(arr, condition):
    left, right = 0, len(arr)
    while left < right:
        mid = (left + right) // 2
        if condition(arr[mid]):
            right = mid        # mid COULD be the answer, search LEFT
        else:
            left = mid + 1     # mid is definitely NOT valid, rule it out
    return left    # left == right; this is the answer
                    # (returns len(arr) if NOTHING satisfies condition)
```

**Pattern 3 — LAST position satisfying condition:**
```
while left < right; right starts at len(arr)-1; mid=(left+right+1)//2 (+1 avoids infinite loop)
if condition True: left=mid (keep mid, search right); else right=mid-1 (discard mid)

def find_last_true(arr, condition):
    left, right = 0, len(arr) - 1
    while left < right:
        mid = (left + right + 1) // 2    # +1 to avoid infinite loop
        if condition(arr[mid]):
            left = mid          # mid COULD be the answer, search RIGHT
        else:
            right = mid - 1     # mid is definitely NOT valid, rule it out
    return left    # left == right; this is the answer
                    # (returns -1 if NOTHING satisfies condition, IF
                    #  you check that arr[left] actually satisfies it)
```