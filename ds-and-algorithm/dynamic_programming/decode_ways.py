'''
def decode_ways_recursive(s, i):
    if i == 0:
        return 1
    if i == 1 and s[i-1] != '0':
        return 1
    dec = 0
    if int(s[i-1]) >= 1:
        dec = decode_ways_recursive(s, i-1)
    if i >= 2 and 10 <= int(s[i-2:i]) <= 26:
        dec += decode_ways_recursive(s, i-2)
    return dec
print(decode_ways_recursive("0", 1))
'''

def decode_ways_recursive1(s, i):
    if i == 0:
        return 1
    dec = 0
    if int(s[i-1]) >= 1:
        dec = decode_ways_recursive1(s, i-1)
    if i >= 2 and 10 <= int(s[i-2:i]) <= 26:
        dec += decode_ways_recursive1(s, i-2)
    return dec
print(decode_ways_recursive1("226", 3))

def decode_ways_recursive2(s, i, mem):
    if i in mem:
        return mem[i]
    if i == 0:
        return 1
    dec = 0
    if int(s[i-1]) >= 1:
        dec = decode_ways_recursive2(s, i-1, mem)
    if i >= 2 and 10 <= int(s[i-2:i]) <= 26:
        dec += decode_ways_recursive2(s, i-2, mem)
    mem[i] = dec
    return dec
print(decode_ways_recursive2("226", 3, {}))

def decode_ways(s):
    table = [0]*(len(s)+1)
    table[0] = 1
    table[1] = 1 if s[0:1] != '0' else 0

    for i in range(2, len(s)+1):
        if 1 <= int(s[i-1]) <= 9:
           table[i] += table[i-1]

        if 10 <= int(s[i-2:i]) <= 26:
            table[i] += table[i-2]
    return table[len(s)]

print(decode_ways("226"))