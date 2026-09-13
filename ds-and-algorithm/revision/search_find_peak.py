def find_peak(arr):
    left = 0
    right = len(arr)-1

    while left < right:
        mid = (left+right+1)//2
        print(f"mid: {mid}, left:{left}, right:{right}")
        if arr[mid-1] > arr[mid]:
            right = mid-1
        else:
            left = mid

        #elif arr[mid+1] > arr[mid]:
        #    left = mid
    
    print(arr[left])
    return left



print(find_peak([1,0,2,4,10]))