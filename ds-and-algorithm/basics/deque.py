from collections import deque

collect = deque()
collect.append(1)
collect.append(2)
collect.append(3)


collect.appendleft(4)
collect.appendleft(4)
collect.appendleft(12)

collect.append((8,9))

print(f"before pop collect: {collect}")

collect.pop()
collect.popleft()

print(f"collect: {collect}")

if 4 in collect:
    print(f"True")

print(f"len: {len(collect)}, collect[0]: {collect[0]}")