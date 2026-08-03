Collision handling techniques:

Technique          How it works          Clustering    Memory
─────────────────────────────────────────────────────────────
Separate chaining  linked list per slot  None          Extra
Linear probing     +1, +2, +3...         High          None
Quadratic probing  +1², +2², +3²...      Medium        None
Double hashing     +hash2, +2*hash2...   Low           None


Quadratic: slot = hash1 + n²
n=1: 3 + 1  = 4
n=2: 3 + 4  = 7
n=3: 3 + 9  = 12

Double hashing uses different step sizes per key — reduces clustering better than quadratic.
Double hashing: slot = hash1 + n×hash2
n=1: 3 + 2  = 5
n=2: 3 + 4  = 7
n=3: 3 + 6  = 9

linear probing: hash1 + n
n=1: 3 + 1  = 4
n=2: 3 + 2  = 5
n=3: 3 + 3  = 6

clustering in linear probing:
Frank needed 4 probes just because of the cluster. As table fills — clusters grow — probes increase — O(1) becomes O(n) in worst case.
hash("frank") = 3 → slot 3 taken
               → try 4 taken
               → try 5 taken
               → try 6 taken
               → try 7 empty → store at 7
Fixed hash range → keys bunch together → clusters form
New keys hitting same range → must probe through entire cluster
More items → bigger clusters → slower lookup

Load Factor — Key Concept:
load factor = number of items / table size
Separate chaining: works fine even above 1.0
Open addressing:   degrades badly above 0.7
When load factor too high → resize table (like dynamic array)

What Python Uses:
Python dict uses open addressing with a variation
of double hashing internally.
Load factor threshold ≈ 0.67
When exceeded → table resized to 2x