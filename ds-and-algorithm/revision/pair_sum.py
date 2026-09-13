
def pair_sum(arr, target):
    diff = {}

    for i in range(len(arr)):
        d = target-arr[i]
        if d in diff:
            return [diff[d], i]
        else:
            diff[arr[i]] = i
    return -1



print(pair_sum([2,9,14,7], 16))
print(pair_sum([1,3,5,7], 8))