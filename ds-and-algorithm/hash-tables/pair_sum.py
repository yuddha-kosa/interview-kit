def two_sum_wrong(nums,target):
    nums.sort() # sorting will change the index position
    left = 0
    right = len(nums)-1

    while left < right:
        sum = nums[left] + nums[right]
        if sum == target:
            return [left, right]
        elif sum < target:
            left += 1
        else:
            right -= 1
    return False

'''
def two_sum(nums,target):

    unique = {}

    for i in range(len(nums)):
        unique[i] = nums[i]
        for key,val in unique.items():
            if nums[i] + val == target:
                return [i,key]
            
    return False
'''

def two_sum(nums, target):
    seen = {}

    for i, num in enumerate(nums):
        diff = target-num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return False



print(two_sum([2,9,14,7], 16))
print(two_sum([1,3,5,7], 8))
print(two_sum([4,6,10], 16))