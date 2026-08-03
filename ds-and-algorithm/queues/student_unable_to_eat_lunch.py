def unable_to_eat(students,sandwiches):

    rejected = 0
    while students:
        stu_choice = students.pop(0)
        san_available = sandwiches[0]
        if stu_choice != san_available:
            students.append(stu_choice)
            rejected += 1
        else:
            sandwiches.pop(0)
            rejected = 0
        if rejected == len(students):
            return len(students)
    return 0

print(unable_to_eat([1,1,0,0], [0,1,0,1]))
print(unable_to_eat([1,1,1,0,0,1], [1,0,0,0,1,1]))

def unable_to_eat1(students, sandwiches):
    from collections import Counter
    count = Counter(students)

    for sandwich in sandwiches:
        if count[sandwich] == 0:
            return sum(count.values())
        count[sandwich] -= 1

    return 0