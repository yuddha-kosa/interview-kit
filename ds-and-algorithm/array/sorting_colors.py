
def sort_colors(arr):
    red = []
    green = []
    blue = []
    result = []
    for i, num in enumerate(arr):
        if num == 0:
            red.append(num)
        if num == 1:
            green.append(num)
        if num ==2:
            blue.append(num)
    for i, num in enumerate(red):
        result.append(num) 
    for i, num in enumerate(green):
        result.append(num)
    for i, num in enumerate(blue):
        result.append(num) 
    return result

print(sort_colors([0,1,2,1,2,0,1,0,2])) 

from collections import defaultdict
def sort_colors2(arr):
    dict_count = defaultdict(int)
    result = []
    for i, num in enumerate(arr):
        dict_count[num] = dict_count.get(num, 0) + 1


    red = dict_count[0] 
    green = dict_count[1] 
    #blue = dict_count[2]

    
    for i in range(len(arr)):
        if i < red:
            arr[i] = 0
        elif i >= red and i < red+green:
            arr[i] = 1
        else:
            arr[i] = 2
    return arr
    #for i in range(red):
    #    result.append(0) 
    #for i in range(green):
    #    result.append(1)
    #for i in range(blue):
    #    result.append(2) 
    #return result

print(sort_colors2([0,1,2,1,2,0,1,0,2])) 
# time: O(n)
# space: ??

def sort_colors3(arr):
    low = 0
    mid = 0
    high = len(arr)-1

    while mid <= high:
        if arr[mid] == 0:
            arr[low],arr[mid] = arr[mid], arr[low] 
            mid += 1
            low += 1
        elif arr[mid] == 1:
            mid += 1
        elif arr[mid] == 2:
            arr[high], arr[mid] = arr[mid], arr[high]
            high -= 1

print(sort_colors3([0,1,2,1,2,0,1,0,2])) 