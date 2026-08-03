def sort_colors(colors):
    left = 0
    mid = 0
    right = len(colors)-1

    while mid <= right:
        if colors[mid] == 0:
            colors[left], colors[mid] = colors[mid], colors[left]
            mid += 1
            left += 1
        elif colors[mid] == 1:
            mid += 1
        else:
           colors[right], colors[mid] = colors[mid], colors[right] 
           right -= 1
    return colors

def sort_colors2(colors):
    clrs = [0]*3
    for i in range(len(colors)):
        clrs[colors[i]] += 1
    
    index = 0
    for i in range(len(clrs)):
        for _ in range(clrs[i]):
            colors[index] = i
            index += 1
    return colors



print(sort_colors([0,1,2,1,2,0,1,0,2])) 
print(sort_colors2([0,1,2,1,2,0,1,0,2])) 