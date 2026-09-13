def find_min(nums):
    left = 0
    right = len(nums)-1

    while left < right:

        mid = (left+right)//2
        if nums[right] < nums[mid]:
            left = mid+1
        else:
            right = mid
    return nums[left]


print(find_min([8,9,10,1,2,3,4,5]))

'''
time: O(log n)
space: O(1)
'''