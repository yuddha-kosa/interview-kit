def three_sum(nums):
    nums.sort()
    result =[]

    for i in range(len(nums)-2):
        # if the current number is same as previous then for previous we have already check all different
        # options, so no need to check again, just continue.
        if i > 0 and nums[i] == nums[i-1]:
            continue
        start = i + 1
        end = len(nums)-1
        while start < end:
            sum = nums[i] + nums[start] + nums[end]

            if sum == 0:
                result.append([nums[i],nums[start], nums[end]])
                # to make sure we don't have duplicate we increment the start until next is not the same number.
                while start < end and nums[start] == nums[start+1]:
                    start += 1
                # given we already incremented start, there is no chance that the current end will produce a 0,
                # because it's a sorted array, and given start will produce a biggern number after incerement,
                # end should produce a smaller number, so it needs to decrease.
                while end > start and nums[end] == nums[end-1]:
                    end -= 1
                # increase start and decrease end.
                start +=1
                end -= 1
            elif sum < 0:
                start += 1
            else:
                end -= 1
    return result

print(three_sum([-3,-2,0,1,2,3]))

print(three_sum([0,0,0,0]))

print(three_sum([1,2,-1,-2]))







