def triplet_sum(arr):
    arr.sort()
    list_set = []
    for i in range(len(arr)-2):
        if i > 0 and arr[i] == arr[i-1]:
            continue
        left = i+1
        right = len(arr)-1
        current = arr[i]
        while left < right:
            sum = current + arr[left] + arr[right] 
            if sum == 0:
                list_set.append([current, arr[left], arr[right]])
                while left < right and arr[left] == arr[left+1]:  
                    left += 1
                while right > left and arr[right] == arr[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif sum < 0:
                left += 1
            else:
                right -=1
    return list(list_set)

print(triplet_sum([-3,-2,0,1,2,3]))

print(triplet_sum([0,0,0,0]))