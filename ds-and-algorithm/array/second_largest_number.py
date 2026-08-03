def second_largest_number(nums):
    largest = nums[0]
    second = float('-inf')

    for i in range(1, len(nums)):
        if nums[i] > largest:
            second = largest
            largest = nums[i]
        else:
            if nums[i] < largest and nums[i] > second:
                second = nums[i]
    return second

print(second_largest_number([100,3,-1,-3,5,3,8, 80, 100,7]))

