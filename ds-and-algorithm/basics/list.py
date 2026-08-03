def list(input, num):
    num.append(input)
    return num

if __name__ == "__main__":
    num = []
    for i in range (10):
        num = list(i, num)
        print(f'num={num}')

    for i in range(len(num)):    
        print(f'i={i}')
        print(f'num={num[i]}')

    for i, n in enumerate(num):
        print(f'i: {i}, n:{n}')

    pop_num = num.pop()
    print(f'pop_num: {pop_num}, num: {num}')

    pop3_num = num.pop(3)
    print(f'pop3_num: {pop3_num}, num: {num}')

    app_num = num.append(0)
    print(f'append_num: {app_num}, num: {num}')

    sort_num = num.sort()
    print(f'sort_num: {sort_num}, num: {num}')

    sort1_num = sorted(num)
    print(f'sort1_num: {sort1_num}, num: {num}')

    rev = num[::-1]
    print(f'reverse: {rev}')