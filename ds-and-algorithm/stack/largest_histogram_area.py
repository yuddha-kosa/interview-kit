def largest_histogram_area(histogram):
    area = 0
    for i in range(len(histogram)):
        min_height = histogram[i]
        for j in range(i, len(histogram)):
            min_height = min(min_height,histogram[j])
            width = j-i+1
            area = max(area, (min_height*width))
    return area

print(largest_histogram_area([2,1,5,6,2,3]))

def largest_histogram_area1(histogram):
    width_of_each_pill = 1
    max_area = 0
    stack = []
    n = len(histogram)
    for i in range(len(histogram)):
        while stack and histogram[i] < histogram[stack[-1]]:
            length = histogram[stack.pop()]
            if stack:
                # i+1 because index is starting from 0, i is the pillar number.
                width = ((i+1)*width_of_each_pill)-width_of_each_pill - (stack[-1]+1)*width_of_each_pill
            else:
                # stack is empty means there is no pillar smaller than the current popped pillar, that
                # means we should use the length of the current popped pillar and width of all the
                # pillar left of current i to calculate the area.
               width = ((i+1)*width_of_each_pill)-width_of_each_pill
            area = length * width
            max_area = max(max_area, area)
        stack.append(i)
    
    while stack:
        length = histogram[stack.pop()]
        if stack:
            # when we are popping at the last means it is the largest in the current stack,
            # and it is at the end, so it will cover width of all the n pillars-width till
            # the 2nd largest pillar.
            # if there is no 2nd largest that means this is the smallest and area should be calcuated
            # using the full width of n pillars.
            width = (n * width_of_each_pill) - (stack[-1]+1)*width_of_each_pill
        else:
            width = n*width_of_each_pill
        area = length*width
        max_area = max(max_area, area)
    return max_area
        


print(largest_histogram_area1([2,1,5,6,2,3]))
