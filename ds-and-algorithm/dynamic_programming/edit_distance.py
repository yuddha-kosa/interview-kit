def edit_distance(text1, text2, t1i, t2i, mem):
    if (t1i, t2i) in mem:
        return mem[(t1i, t2i)]
    if t1i == 0:
        return t2i
    if t2i == 0:
        return t1i
    
    ch1 = text1[t1i-1]
    ch2 = text2[t2i-1]

    if ch1 == ch2:
        result = edit_distance(text1, text2, t1i-1, t2i-1, mem)
        mem[(t1i, t2i)] = result
        return result
    
    add_c = edit_distance(text1, text2, t1i, t2i-1, mem)
    del_c = edit_distance(text1, text2, t1i-1, t2i, mem)
    rep_c = edit_distance(text1, text2, t1i-1, t2i-1, mem)

    edit_dist = 1 + min(add_c, del_c, rep_c)
    mem[(t1i, t2i)] = edit_dist
    return edit_dist

print(edit_distance("horse", "ros", len("horse"), len("ros"), {}))

def edit_distance_dp(text1, text2):
    t1i = len(text1)
    t2i = len(text2) 
   
    table = [[0]* (t2i+1) for _ in range(t1i+1)]
   
    for i in range(t1i+1):
        table[i][0] = i

    for j in range(t2i+1):
        table[0][j] = j
   
    for first in range(1, t1i+1):
        for sec in range(1, t2i+1):
            #print(f"first: {first}, sec: {sec}")
            #print(f"table: {table}")
            if text1[first-1] == text2[sec-1]:
                table[first][sec] = table[first-1][sec-1]
            else:
                add_c = table[first][sec-1] # add
                del_c = table[first-1][sec] # del
                rep_c = table[first-1][sec-1] # rep
                table[first][sec] = 1+ min(add_c, del_c, rep_c)
    
    print(f"last table: {table}")
    return table[t1i][t2i]




print(edit_distance_dp("horse", "ros"))