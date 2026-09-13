def building_sky_line(heights):

    stack = []
    result = [-1]*(len(heights))

    for i in range(len(heights)):

        while stack and heights[i] > heights[stack[-1]]:
            result[stack[-1]] = i-stack[-1]
            stack.pop()
        stack.append(i)

    return result



heights = [4, 2, 3, 1, 5, 2]
print(building_sky_line(heights))