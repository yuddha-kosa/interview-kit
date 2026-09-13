'''
Layer 1: Table Array
[
  0: [ ],
  1: [  <-- Layer 2: Bucket Array
       ["apple", 5],   <-- Layer 3: Pair Array (Len 2)
       ["banana", 2]   <-- Layer 3: Pair Array (Len 2)
     ],
  2: [ ],
  ...
]

'''
class HashTable:
    def __init__(self, size=10):
        self.size  = size
        self.table = [[] for _ in range(size)]
    # Data structure: array of array of array: first a table which is array...at each position
    # it has bucket as value which is also an array and each element of the bucket
    # is an array with fixed length 2(key and value).
    def hash(self, key):
        return len(key) % self.size

    def set(self, key, value):
        slot   = self.hash(key)
        bucket = self.table[slot]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])

    def get(self, key):
        slot   = self.hash(key)
        bucket = self.table[slot]
        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        return None

    def delete(self, key):
        slot   = self.hash(key)
        bucket = self.table[slot]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                bucket.pop(i)
                return True
        return False

# Test
ht = HashTable()
ht.set("alice", 25)
ht.set("carol", 30)
ht.set("bob", 20)

print(ht.get("alice"))     # 25
print(ht.get("carol"))     # 30
ht.delete("alice")
print(ht.get("alice"))     # None