def sorting_color(arr):

    count = [0]*3

    for i in range(len(arr)):
        count[arr[i]] += 1
    
    result = []
    for j in range(len(count)):
        for _ in range(count[j]):
            result.append(j)
    return result

print(sorting_color([0,1,2,1,0,0,1,2,2]))

'''
time: O(n+k)
space: O(n)
'''
