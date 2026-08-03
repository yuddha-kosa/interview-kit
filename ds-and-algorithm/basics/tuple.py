point = (3, 4)

point[0]
print(f"point 0: {point[0]}")

a, b = point
print(f"a, b: {a, b}")
print(f"a: {a}, b: {b}")
b, a= a, b
print(f"a: {a}, b: {b}")

coordinates = [("a", 1), ("c", 2), ("b", 3)]
coordinates.sort()
print(f"coordinates: {coordinates}")

coordinates.sort(key=lambda x:x[1])
print(f"coordinates: {coordinates}")

def closest_points(points, k):
    distances = []
    for x, y in points:
        distances.append((x**2 + y**2, x,y))
    distances.sort(key=lambda x:x[0])

    #return [(a,b) for _, a, b in distances[:k]]
    # or
    short_dist = []
    for _, a, b in distances[:k]:
        short_dist.append((a,b))
    return short_dist 



points = [(3,3), (1,1), (5,5), (0,1)]
print(closest_points(points, 2))   