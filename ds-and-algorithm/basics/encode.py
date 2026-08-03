chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num):
    result = ""
    while num > 0:
        print(f"num: {num}") 
        #print(f"result: {result}")  
        result = chars[num % 62] + result
        print(f"num % 62: {num % 62}")  
        print(f"result: {result}") 
        num //= 62
        print(f"num//: {num}") 
    return result

res1 = encode(100001)  #  "q0T"
#res2 = encode(100002)  #  "q0U"  # next ID, completely different

print(f"res1: {res1}")
#print(f"res2: {res2}")