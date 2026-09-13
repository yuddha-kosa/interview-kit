Given the tight timeline, let's build this as a genuinely fast, comprehensive reference — verified for accuracy, not a teaching exercise.# Python DSA Cheat Sheet

---

## String methods

```python
s.isdigit()      # True if ALL chars are digits (0-9)
s.isalpha()      # True if ALL chars are letters
s.isalnum()      # True if ALL chars are letters OR digits
s.isupper() / s.islower()
s.upper() / s.lower()
s.strip()        # remove leading/trailing whitespace
s.split(",")     # -> list, split on delimiter (default: whitespace)
s.split()        # split on ANY whitespace, ignores extras
"".join(lst)     # combine list of strings into ONE string
s.replace(old, new)
s.find(sub)      # returns index, or -1 if not found
s.index(sub)     # like find, but RAISES an error if not found
s[::-1]          # reverse a string (slicing trick)
s.count(sub)     # count occurrences
ord('a')         # char -> ASCII/Unicode code point (97)
chr(97)          # code point -> char ('a')
```

---

## List methods

```python
lst.append(x)         # add ONE item to the end
lst.extend([a,b])      # add MULTIPLE items (unpacks the iterable)
lst.insert(i, x)       # insert at specific index
lst.pop()              # remove & return LAST item
lst.pop(i)             # remove & return item at index i
lst.remove(x)          # remove FIRST occurrence of value x (by value, not index)
lst.reverse()          # reverse IN PLACE, returns None
lst[::-1]              # reverse via slicing, returns a NEW list
lst.sort()             # sort IN PLACE, returns None
sorted(lst)            # returns a NEW sorted list, original UNCHANGED
lst.sort(reverse=True) # descending
lst.sort(key=lambda x: x[1])   # sort by custom key
lst.index(x)           # find index of FIRST occurrence
x in lst               # membership check, O(n)
lst.count(x)
```

---

## Dict methods

```python
d.get(key, default)       # safe lookup, no KeyError
d.get(key, 0) + 1          # common pattern for counting
d.setdefault(key, [])      # get value, or SET+return default if missing
d.keys() / d.values() / d.items()
key in d                   # membership check, O(1)
d.pop(key)                 # remove and return value
{k:v for k,v in d.items() if condition}   # dict comprehension
```

---

## Set methods

```python
s.add(x)
s.remove(x)      # raises KeyError if not present
s.discard(x)     # does NOT raise if not present
x in s            # O(1) membership check (fast, unlike list)
s1 & s2           # intersection
s1 | s2           # union
s1 - s2           # difference
```

---

## Common built-in functions

```python
len(x)
abs(x)
min(x) / max(x)
sum(iterable)
sorted(iterable, key=..., reverse=...)
reversed(iterable)       # returns an ITERATOR, not a list
enumerate(lst)            # -> (index, value) pairs
zip(lst1, lst2)            # pairs elements from multiple iterables
map(func, iterable)
filter(func, iterable)
any(iterable)              # True if ANY element is truthy
all(iterable)              # True if ALL elements are truthy
range(start, stop, step)
divmod(a, b)               # -> (a//b, a%b) in one call
```

---

## Useful modules

```python
from collections import deque, Counter, defaultdict

deque()               # O(1) append/pop from BOTH ends
Counter(lst)           # frequency count, dict-like
defaultdict(list)      # auto-creates missing keys with a default

import heapq
heapq.heapify(lst)
heapq.heappush(heap, x)
heapq.heappop(heap)

import math
math.gcd(a,b)
math.sqrt(x)
math.inf              # infinity, safer than float('inf') in some contexts

from itertools import permutations, combinations
```

---

## Key gotchas verified above (worth remembering)

```
sorted(lst)   -> NEW list, original UNCHANGED
lst.sort()    -> sorts IN PLACE, returns None (don't do lst=lst.sort())

s.isdigit()   -> True only if ALL characters are digits
s.isalnum()   -> True if letters OR digits (broader than isdigit)
```

Want the next piece — **Searching, Sorting, Two Pointers, Sliding Window as concepts** — or should we keep drilling this cheat sheet first?