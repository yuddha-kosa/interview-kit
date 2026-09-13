def valid_anangrams(s, p):

    s_map = {}

    for ch in s:
        s_map[ch] = s_map.get(ch, 0) + 1
    
    for cha in p:
        if cha in s_map:
            s_map[cha] -= 1
            if s_map[cha] == 0:
                del(s_map[cha])
    
    if len(s_map) == 0:
        return True
    return False


print(valid_anangrams("listen", "silent"))
print(valid_anangrams("hello", "world"))
