def two_sum_sorted(nums,target):
    i = 0
    j = len(nums)-1
    while i < j:
        current = nums[i] + nums[j] 

        if current == target:
            return [i+1, j+1]
        elif current < target:
            i += 1
        else:
            j -= 1

print(two_sum_sorted([1,2,5,7,11], 8))
print(two_sum_sorted([3,4,6,8], 10))