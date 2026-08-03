

def shift_up(arr):
    c = len(arr)-1

    while True:

        i = (c-1)//2
        if i >= 0 and arr[c] < arr[i]:
            arr[i], arr[c] = arr[c], arr[i]
        else:
            break
        c = i

def insert(arr, val):
    arr.append(val)
    shift_up(arr)
    return arr

print(insert([-2, 1, 5, 9, 4, 6, 7], 3))

'''
 time: O(log n)
 space: O(1)
'''
def shift_down(arr):
    n = len(arr)
    i = 0
    while True:
        left = 2*i + 1
        right = 2*i + 2
        smallest = i
        if left < n and arr[left] < arr[smallest]:
            smallest = left
        if right < n and arr[right] < arr[smallest]:
            smallest = right
        if i == smallest:
            break
        arr[i], arr[smallest] = arr[smallest], arr[i]
        i = smallest

def delete(arr):
    if len(arr) == 0:
        return "nothing to delete"
    last_element = arr.pop()
    if len(arr) > 0:
        arr[0] = last_element
        shift_down(arr)
    return arr

print(delete([-2, 1, 5, 9, 4, 6, 7]))

'''
 time: O(log n)
 space: O(1)

'''