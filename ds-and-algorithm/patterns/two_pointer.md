Ask: "What must be true for one more iteration to be safe?"

Odd-even:
    Need even and even.next to exist → safe to do one more step
    → while even and even.next

Two sum sorted:
    Need left < right → two different elements to compare
    → while left < right

Merge two lists:
    Need both lists to have elements → compare heads
    → while l1 and l2



The < vs <= confusion:
left < right:   two DIFFERENT elements needed
                stop when they meet (one element left)

left <= right:  same element is valid
                stop when they cross

Simple rule:
Comparing TWO elements → left < right
Processing ONE element at a time → left <= right