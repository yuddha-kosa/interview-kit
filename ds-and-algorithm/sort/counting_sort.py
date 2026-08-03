# create an array of length equal to the maximun number
# iterate over the array and store the count of occurence of each number
# map the index as the number and in value keep the count.
# loop over the count_array and create the new sorted array.
def count_sort(arr):
    max_num = max(arr)

    count_arr = [0]*(max_num+1)

    for i in range(len(arr)):
        count_arr[arr[i]] += 1 
    
    print(f"count_arr: {count_arr}")
    
    result = []
    for i in range(len(count_arr)):
        for _ in range(count_arr[i]):
            result.append(i)
    return result

print(count_sort([4, 2, 2, 8, 3, 3, 1]))
print(count_sort([0,3,1,5,2,7,8,4]))

print("******************************")
'''
15 = 10
14 = 9
9 = 4
8 = 3
5 = 0
'''
def count_sort1(arr):
    max_num = max(arr)
    min_num = min(arr)

    count_arr = [0]*(max_num-min_num+1)

    for i in range(len(arr)):
        count_arr[arr[i]-min_num] += 1 
    
    print(f"count_arr: {count_arr}")
    
    result = []
    for i in range(len(count_arr)):
        print(f"i:{i}, min_num: {min_num}, count_arr[{i+min_num}]: {count_arr[i]}, i+min_num: {i+min_num}")
        for _ in range(count_arr[i]):
            #print(f"i:{i}, min_num: {min_num}, count_arr[{i}]: {count_arr[i]}, i+min_num: {i+min_num}")
            result.append(i+min_num)
    return result

print(count_sort1([4, 2, 2, 8, 3, 3, 9]))
#print(count_sort1([0,3,1,5,2,7,8,4]))
#print(count_sort1([0,3,1,5,2,7,8,4,-1,-2,-1]))