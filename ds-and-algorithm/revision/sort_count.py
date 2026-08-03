def count_sort(arr):

    min_arr = min(arr)
    max_arr = max(arr)
    count_arr = [0]*(max_arr-min_arr+1)

    for i in range(len(arr)):
        count_arr[arr[i]-min_arr] += 1
    result = []
    for num in range(len(count_arr)):
        for _ in range(count_arr[num]):
            result.append(num+min_arr)
    return result

print(count_sort([5, 3, 8, 1, 2]))
print(count_sort([0,3,1,5,2,7,8,4]))
print(count_sort([10,30,1,5,20,70,8,4]))
print(count_sort([1,2,3,4,5]))