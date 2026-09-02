def single_number(nums):
    result = 0
    for i in range(len(nums)):
        result = result^nums[i]
    return result


print(single_number([3,2,3]))
print(single_number([7,6,6,7,8]))


'''
Time:  O(n)
Space: O(1)
'''