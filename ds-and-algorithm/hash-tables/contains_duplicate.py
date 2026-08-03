def contains_duplicate(arr):

    hash_dup = {}
    for num in arr:
        if num in hash_dup:
            return True
        else:
            hash_dup[num] = True
    return False

print(contains_duplicate([2,7,8,2]))
print(contains_duplicate([10,20,30,40]))
