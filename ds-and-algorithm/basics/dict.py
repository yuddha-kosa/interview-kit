def add_to_dict(key, val, m: dict) -> dict:
    m[key] = val
    return m

if __name__ == "__main__":
    m = {}
    for i in range(3):
        m = add_to_dict(i, i, m)
        print(f'map/dict={m}')
    add_to_dict("fruit", "apple", m)
    add_to_dict("animal", "rabbit", m)

    fruit = m.get("fruit")
    print(f"fruit: {fruit}")

    m["number"] = m.get("number", 0) + 1
    m["number"] = m.get("number", 0) + 1

    m["number2"] = m.get("number2", 0) + 1
    for key, val in m.items():
        print(f"key: {key}, value: {val}")

    if "number" in m:
        print(f"true")

countchar = {}
for c in "leetcode":
    countchar[c] = countchar.get(c, 0) + 1
print(f"countchar: {countchar}")