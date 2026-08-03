
def sum(num):
    if len(num) == 0:
        return 0
    #if len(num) == 1:
    #    return num[0]
    
    return num[0] + sum(num[1:])

s = sum([1,6,5,4,3,2,7,8,9,10])
#s = sum([])

print(f"sum: {s}")