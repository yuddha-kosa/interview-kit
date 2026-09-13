
def is_bad(n):
    if n >=4:
        return True
    return False

def first_bad_version(num):

    left = 0
    right = num

    while left < right:

        mid = (left+right)//2

        if not is_bad(mid):
            left = mid+1
        else:
            right = mid 
    return left

print(first_bad_version(5))

def last_good_version(num):

    left = 0
    right = num

    while left < right:

        mid = (left+right+1)//2
        print(f"mid: {mid}, left:{left}, right:{right}")

        if not is_bad(mid):
            left = mid
        else:
            right = mid-1 
    return left

print(last_good_version(3))


'''
Since // rounds DOWN, mid is always "biased toward left" —
specifically, when left and right are adjacent, mid EQUALS
left, never right.

This means:
    "right = mid"  -> ALWAYS shrinks right (mid is always
                      SMALLER than the old right) -> ALWAYS progress

    "left = mid"   -> when mid happens to EQUAL left (the
                      adjacent case), this is a NO-OP ->
                      INFINITE LOOP RISK

The +1 fix (mid=(left+right+1)//2) shifts mid's rounding
BIAS toward RIGHT instead of left — so NOW, when left and
right are adjacent, mid lands on RIGHT, guaranteeing
"left=mid" also makes real progress.
'''