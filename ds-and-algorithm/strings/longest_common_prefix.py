def longest_common_prefix(texts):
    longest = texts[0]

    for i in range(1, len(texts)):
        # compare
        current = []
        if longest == "":
            break
        for j in range(len(longest)):
            print(f"longest[i]: {longest[j]}, texts[i][j]: {texts[i][j]}")
            if len(texts[i])-1 >= j  and longest[j] == texts[i][j]:
                current.append(longest[j])
            else:
                longest = "".join(current)
                break
    return longest




print(longest_common_prefix(["interview", "interval", "internet"]))
print(longest_common_prefix(["hello", "world", "hi"]))