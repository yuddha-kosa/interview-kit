def comb_sum(nums, target):

    results = []
    path = []

    def backtrack(start):

        if sum(path) > target:
            return
        if sum(path) == target:
            results.append(path[:])
            return
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i)
            path.pop()

    backtrack(0)
    return results


print(comb_sum([2, 3, 6, 7], 7))


'''
backtrack(0)                    path = []

    for i = 0
        path.append(2)          path = [2]

        backtrack(0)

            for i = 0
                path.append(2)  path = [2,2]

                backtrack(0)

                    for i = 0
                        path.append(2)  path = [2,2,2]

                        backtrack(0)

                            for i = 0
                                path.append(2)  path = [2,2,2,2]

                                backtrack(0)

                                    sum(path)=8 > 7
                                    return

                                path.pop()      path = [2,2,2]

                            for i = 1
                                path.append(3)  path = [2,2,2,3]

                                backtrack(1)

                                    sum(path)=9 > 7
                                    return

                                path.pop()      path = [2,2,2]

                            for i = 2
                                path.append(6)  path = [2,2,2,6]

                                backtrack(2)

                                    sum(path)=12 > 7
                                    return

                                path.pop()      path = [2,2,2]

                            for i = 3
                                path.append(7)  path = [2,2,2,7]

                                backtrack(3)

                                    sum(path)=13 > 7
                                    return

                                path.pop()      path = [2,2,2]

                        return

                    path.pop()      path = [2,2]

                    for i = 1
                        path.append(3)  path = [2,2,3]

                        backtrack(1)

                            sum(path)=7
                            results.append([2,2,3])
                            return

                        path.pop()      path = [2,2]

                    for i = 2
                        path.append(6)

                        backtrack(2)

                            sum(path)=10 > 7
                            return

                        path.pop()

                    for i = 3
                        path.append(7)

                        backtrack(3)

                            sum(path)=11 > 7
                            return

                        path.pop()

                return

            path.pop()      path = [2]

            for i = 1
                path.append(3)      path = [2,3]

                backtrack(1)

                    ...
'''