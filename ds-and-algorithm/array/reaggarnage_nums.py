from collections import deque
def rearrange_nums(nums):

    new_num = []
    positive_num = deque()
    neg_num = deque()
    for i in range(len(nums)):
        if nums[i] >= 0:
            positive_num.append(nums[i])
        else:
            neg_num.append(nums[i])
    
    #for i in range(len(positive_num)):
    while positive_num: 
        new_num.append(positive_num.popleft()) 
        #if len(neg_num) > 0:
        if neg_num: 
            new_num.append(neg_num.popleft()) 
    
    #if len(neg_num) > 0:
    while neg_num: 
        for i in range(len(neg_num)):
            new_num.append(neg_num.popleft()) 

    return new_num
print(rearrange_nums([1,2,3,-4,-1,4]))
print(rearrange_nums([-5, -2, 5, 2, 4, 7, 1, 8, 0, -8]))

#time: O(n)
#space: O(n)


'''
********

from collections import deque

def rearrange_nums(nums):

    new_num = []

    positive_num = deque()

    neg_num = deque()

    for i in range(len(nums)):

        if nums[i] >= 0:

            positive_num.append(nums[i])

        else:

            neg_num.append(nums[i])

    

    for i in range(len(positive_num)):

        print(f"len pos: {len(positive_num)}")

        #new_num.append(positive_num[i])

        #positive_num.popleft()

        new_num.append(positive_num.popleft()) 

        if len(neg_num) > 0:

            print(f"len neg: {len(neg_num)}")

            #new_num.append(neg_num[i])

            #neg_num.popleft()

            new_num.append(neg_num.popleft()) 

    

    if len(neg_num) > 0:

        for i in range(len(neg_num)):

            #new_num.append(neg_num[i])

            #neg_num.popleft()

            new_num.append(neg_num.popleft()) 

    return new_num

print(rearrange_nums([1,2,3,-4,-1,4]))

print(rearrange_nums([-5, -2, 5, 2, 4, 7, 1, 8, 0, -8]))

#time: O(n)

#space: O(n)
'''