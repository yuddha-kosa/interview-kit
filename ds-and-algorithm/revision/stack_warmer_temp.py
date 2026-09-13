def warmer_temp(temp):

    dec_stack = []
    result = [0]*(len(temp))

    for i in range(len(temp)):
        if len(dec_stack) == 0:
            dec_stack.append((temp[i], i))
        else:
            # fetch the top element and compare
            top_temp, _ = dec_stack[-1]
            while top_temp < temp[i]:
                t, index = dec_stack.pop()
                result[index]=(i-index)
                if len(dec_stack) == 0:
                    break
                top_temp, _ = dec_stack[-1]
            
            dec_stack.append((temp[i], i))
        print(dec_stack)
        
    return result

            

print(warmer_temp([73,74,75, 71,69,72,76,73]))