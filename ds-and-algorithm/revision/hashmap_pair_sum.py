def pair_sum(arr, target):
    seen = {}
    for i in range(len(arr)):
        comp = target-arr[i]
        if comp in seen:
            return [i, seen[comp]]
        seen[arr[i]] = i
    return False

print(pair_sum([2,9,14,7], 16))
print(pair_sum([1,3,5,7], 8))
print(pair_sum([4,6,10], 16))
