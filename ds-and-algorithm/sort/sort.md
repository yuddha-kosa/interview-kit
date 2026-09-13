Algorithm         Time (avg)      Time (worst)    Space
Bubble Sort       O(n²)           O(n²)           O(1)
Selection Sort    O(n²)           O(n²)           O(1)
Insertion Sort    O(n²)           O(n²)           O(1)
Merge Sort        O(n log n)      O(n log n)      O(n)
Quick Sort        O(n log n)      O(n²)           O(log n) avg, O(n) worst
Heap Sort         O(n log n)      O(n log n)      O(1)
Count Sort         O(n + k)        O(n + k)        O(n)


Bubble:    repeatedly swap ADJACENT out-of-order pairs, largest
           "bubbles up" to the end each pass

Selection: repeatedly find the MINIMUM in the unsorted portion,
           swap it to the front

Insertion: build up a sorted portion one element at a time,
           INSERTING each new element into its correct position

Merge:     divide array in half repeatedly, sort each half,
           MERGE them back together (same pattern as your
           Merge Sort complexity derivation months ago)

Quick:     pick a PIVOT, partition everything smaller to its
           left and larger to its right, recursively sort each side

Heap:      build a max-heap from the array, repeatedly extract
           the max and place it at the end