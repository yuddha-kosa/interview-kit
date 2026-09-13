def target_pair_sum(arr, target):
    arr.sort()
    result = []

    left = 0
    right = len(arr)-1

    while left < right:
        sum = arr[left] + arr[right]

        if sum == target:
            if (arr[left] & arr[right]) == 0:
                result.append((left, right))
            left += 1
            right -= 1
        elif sum > target:
            right -= 1
        else:
            left += 1
    print(result)
    return (len(result))



nums = [1, 2, 3, 4, 5]
k = 5

print(target_pair_sum(nums, k))
