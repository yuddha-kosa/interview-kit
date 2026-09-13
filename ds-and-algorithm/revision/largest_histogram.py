def largest_histogram(histogram):

    stack = []
    max_area = 0
    n = len(histogram)

    for i in range(len(histogram)):

        while stack and histogram[i] < histogram[stack[-1]]:
            length = histogram[stack.pop()]
            if stack:
                width = i-stack[-1]-1
            else:
                width = i
            max_area = max(max_area, (length*width))
        stack.append(i)

    while stack:
        length = histogram[stack.pop()]
        if stack:
            width = n-stack[-1]-1
        else:
            width = n
        max_area = max(max_area, (length*width))

    return max_area




print(largest_histogram([2,1,5,6,2,3]))