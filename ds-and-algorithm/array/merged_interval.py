def merge_intervals(arr):

    arr.sort(key=lambda x: x[0])
    merged = [arr[0]]

    for current in arr:
        left_interval = merged[-1]
        # if last element of left is greater than first element of right then merge.
        if left_interval[1] > current[0]:
            left_interval[1] = max(left_interval[1], current[1])
            merged[-1] = left_interval
        else:
            merged.append(current)
    
    return merged




# Example Usage:
example_input = [[1, 3], [2, 6], [8, 10], [15, 18]]
print(merge_intervals(example_input))
# Output: [[1, 6], [8, 10], [15, 18]]