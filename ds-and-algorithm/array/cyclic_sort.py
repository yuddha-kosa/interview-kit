
def missing_num(arr):
    index = 0
    right = len(arr)

    while index < right:
        correct_index = arr[index]
        if  correct_index < right and correct_index != index:
            arr[correct_index], arr[index] = arr[index], arr[correct_index]
        else:
            index += 1

    print(arr)
    for i in range(len(arr)):
        if i != arr[i]:
            return i 


print(missing_num([3,0,1]))

'''
Find the Duplicate Number (Range: 1 to n)In this variation (LeetCode 287), 
an array of length n + 1 contains integers from 1 to n.
There is exactly one duplicate number, meaning two numbers will fight for the same correct slot.
'''
def find_duplicate_number(nums):
    i = 0
    while i < len(nums):
        # The index where nums[i] belongs
        correct_index = nums[i] - 1
        
        # If the current number is not in its correct slot
        if i != correct_index:
            # Check if the correct slot already has this exact number
            if nums[i] == nums[correct_index]:
                return nums[i]  # Found the duplicate immediately!
            
            # Otherwise, swap them into their proper places
            nums[i], nums[correct_index] = nums[correct_index], nums[i]
        else:
            i += 1
            
    return -1

# Example Trace:
print(find_duplicate_number([1, 3, 4, 2, 2])) 
# Output: 2

