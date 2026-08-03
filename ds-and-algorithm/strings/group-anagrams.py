def group_anagrams(arr):
    seen = set()
    group = []
    for i in range(len(arr)):
        text1 = arr[i]
        current = []
        if text1 in seen:
            continue
        current.append(text1)
        seen.add(text1)
        for j in range(i+1, len(arr)):
            text2 = arr[j]
            if is_anagram(text1, text2):
                current.append(text2)
                seen.add(text2)
        group.append(current)
    return group



def is_anagram(text1, text2):
    if len(text1) != len(text2):
        return False
    count = {}
    for ch in text1:
        count[ch] = count.get(ch,0)+1
    for ch in text2:
        count[ch] = count.get(ch,0)-1
        if count[ch] < 0:
            return False
    return True

print(group_anagrams(["star", "rats", "car", "arc", "arts"]))





def group_anagrams1(arr):

    grouped_anagrams = {}

    for word in arr:
        count = [0]*26
        for ch in word:
            count[ord(ch)-ord('a')] += 1
        if tuple(count) not in grouped_anagrams:
            grouped_anagrams[tuple(count)] = []
        grouped_anagrams[tuple(count)].append(word)
    return list(grouped_anagrams.values())

print(group_anagrams1(["star", "rats", "car", "arc", "arts"]))

def group_anagrams2(arr):
    grouped = {}
    for word in arr:
        count = {}
        for ch in word:
            count[ch] = count.get(ch, 0) + 1
        key = frozenset(count.items())
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(word)
    return list(grouped.values())

# A set by definition has no order.
# {1, 2, 3} == {3, 2, 1} — always true for sets.

# Python computes frozenset hash based on ELEMENTS only
# not their order.

# Same elements → same hash → same dict key ✓

# fs1 = frozenset({('s',1), ('t',1), ('a',1), ('r',1)})
# fs2 = frozenset({('r',1), ('a',1), ('t',1), ('s',1)})

# fs1 == fs2    # True ✓
# hash(fs1) == hash(fs2)    # True ✓