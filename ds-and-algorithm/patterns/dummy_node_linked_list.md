1. Head might change:
Removing head, inserting before head
→ dummy.next always tracks real head
→ no special case needed

Example: remove nth node, merge lists

2. Building a new list from scratch:
You don't know what head will be yet
→ start with dummy, attach nodes
→ return dummy.next at end

Example: add two numbers, merge lists

3. Simplifying edge cases:
Without dummy: check if head is None constantly
With dummy: just use current.next, dummy handles it

Example: any list construction problem

Don't need dummy node when:
→ Just traversing — not modifying head
→ Reversing in place — head known from start
→ Finding middle — head unchanged
→ Palindrome check — head unchanged

Simple rule:
Ask: "Could head change or be unknown?"
Yes → use dummy node
No  → don't need it


Pattern:
dummy = ListNode(0)
current = dummy

# build list...
current.next = node
current = current.next

return dummy.next    # real head