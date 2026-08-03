import heapq


def merge_sorted_list(lists):
    result = []
    heap = []
    for i, lst in enumerate(lists):
            heapq.heappush(heap, (lst[0], 0, i))

    while heap:
        smallest, idx, lst_idx  = heapq.heappop(heap)
        result.append(smallest)

        # we need to retrieve the next element from the same list which
        # gave us the smallest element and after retrieving it we will
        # push it in the heap.
        next_idx = idx+1
        if len(lists[lst_idx]) > next_idx: 
            next_element = lists[lst_idx][next_idx]
            heapq.heappush(heap, (next_element, next_idx, lst_idx))

    return result



lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
result = merge_sorted_list(lists)
print(f"result: {result}")


'''
lists = [[1, 4, 7], [2, 3, 8], [5, 6, 9]]

1,2,5          

                                                        res =[1, 2, 3, 4, 5, 6, 7, 8, 9]

1- pop 

2,5,4



2-pop

5,4,3 -> 3,4,5



3- pop

4,5,8 



4- pop

5,8,7



5-pop

8,7,6 -> 6,7,8



6-pop

7,8,9



7- pop



8- pop



9-pop


'''