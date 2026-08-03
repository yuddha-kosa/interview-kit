def brute_force_pattern_matching(text, pattern):

    pattern_len = len(pattern)

    text_window = []
    for i in range(pattern_len):
        text_window.append(text[i])        

    if pattern == "".join(text_window):
        return 0

    print(f"pattern: {pattern}, text_window: {text_window}")
    for i in range(pattern_len, len(text)):
        # update window
        text_window.append(text[i])
        # shrink window
        #text_window = text_window[len(text_window)-pattern_len:]
        text_window = text_window[1:]

        #print(f"pattern: {pattern}, text_window: {text_window}")

        if pattern == "".join(text_window):
            return i-pattern_len+1
    return -1
print(brute_force_pattern_matching("thigraaprogram", "gram"))

print("*************")
def brute_force_pattern_matching1(text, pattern):

    pattern_len = len(pattern)

    for i in range(len(text)-pattern_len+1):
        if text[i:i+pattern_len] == pattern:
            return i
    return -1
print(brute_force_pattern_matching1("thigraaprogram", "gram"))