
def triplet_sum(arr):

    result = []
    arr.sort()

    for left in range(len(arr)-2):
        if left > 0 and arr[left] == arr[left-1]:
            continue

        mid = left+1
        right = len(arr)-1

        while mid < right:
            sum = arr[left] + arr[mid] + arr[right]

            if sum == 0:
                result.append((arr[left], arr[mid], arr[right]))
                mid += 1
                right -= 1
                while arr[mid] == arr[mid-1] and mid < right:
                    mid += 1
                while arr[right] == arr[right+1] and mid < right:
                    right -=1 
            elif sum > 0:
                right -= 1
            elif sum < 0:
                mid += 1
    
    return result





print(triplet_sum([-3,-2,0,1,2,3]))