def search_in_rot_array(nums,val):

    left = 0
    right = len(nums)-1

    while left <= right:
        mid = (left+right)//2
        if nums[mid] == val:
            return mid
        if nums[mid] > nums[left]:
            if nums[left] <= val < nums[mid]:
                right = mid-1
            else:
                left = mid + 1
        else:        
            if nums[mid] < val <= nums[right]:
                left = mid+1
            else:
                right = mid-1

    return -1


print(search_in_rot_array([6,7,8,1,2,3,4], 8))
print(search_in_rot_array([6,7,8,1,2,3,4], 3))
print(search_in_rot_array([3,4,5,1,2], 7))
print(search_in_rot_array([5], 5))