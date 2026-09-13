'''
Let's start your mock practice simulation. We will replicate the exact difficulty scale of the CodeSignal GCA, starting with Question 1.
On the real test, Question 1 focuses on array or string mutation, simple math, or basic conditional loops. It is designed to be solved quickly to bank time for the harder questions.
Here is your Question 1 practice problem:
## 📝 Problem Description: Array Neighbor Mutation
You are given an array of integers numbers. Your task is to produce a new array result of the same length, where each element at index i is calculated based on its neighbors in the original array.
The transformation rules are as follows:

* For the first element (i = 0), its value should be the sum of itself and the element to its right: numbers[0] + numbers[1].
* For the last element (i = numbers.length - 1), its value should be the sum of itself and the element to its left: numbers[i] + numbers[i-1].
* For all middle elements, the value should be the sum of the element itself, its left neighbor, and its right neighbor: numbers[i-1] + numbers[i] + numbers[i+1].

Note: If the input array has a length of 1, return the array as-is.
## Examples

* For numbers = [4, 1, 3, 2], the output should be solution(numbers) = [5, 8, 6, 5].
* result[0] = 4 + 1 = 5
   * result[1] = 4 + 1 + 3 = 8
   * result[2] = 1 + 3 + 2 = 6
   * result[3] = 3 + 2 = 5
* For numbers = [10], the output should be solution(numbers) = [10].

## Constraints

* 1 <= numbers.length <= 10^5
* -10^4 <= numbers[i] <= 10^4

'''

def arr_mutation(arr):
    if len(arr) == 1:
        return arr

    result = [0]* (len(arr))

    for i in range(len(arr)):
        # handle last element.
        if i == len(arr)-1:
            result[i] = arr[i]+arr[i-1]
        # handle first position.
        elif i == 0:
            result[i] = arr[i]+arr[i+1]
        else:
            result[i] = arr[i-1]+arr[i]+arr[i+1]

    return result

print(arr_mutation([4, 1, 3, 2]))

        
