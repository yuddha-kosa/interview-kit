def daily_temperatures(temp_data):
    stack = []
    result = [0]*len(temp_data)
    for i in range(len(temp_data)):
        if not stack:
            stack.append(i) # store the ith day number starting day 0.
        else:
            if temp_data[i] <= temp_data[stack[-1]]:
                stack.append(i)
            else:
                while stack and temp_data[i] > temp_data[stack[-1]]:
                    day = stack.pop()
                    result[day] = i-day
                stack.append(i)
    return result

print(daily_temperatures([73,74,75,71,69,72,76,73]))
print(daily_temperatures([73,74,75,71,69,72,73]))

def daily_temperatures1(temp_data):
    stack = []
    result = [0]*len(temp_data)
    # Cleaner — same logic
    for i in range(len(temp_data)):
        while stack and temp_data[i] > temp_data[stack[-1]]:
            day = stack.pop()
            result[day] = i - day
        stack.append(i) 
    return result
'''
The trigger to recognize monotonic stack problems:

"Find next greater/smaller element"
"How long until something larger/smaller"
"Largest rectangle" 
"Trapping rain water"

Any problem where:
→ you need to find something ahead
→ and elements "wait" until they find their answer
→ = monotonic stack


The monotonic stack invariant:
Stack always maintains indices in order of
DECREASING temperatures (from bottom to top).

When new temp breaks this order → resolve and pop.
This is what makes it "monotonic" (one direction).

"Stack stores unresolved days in decreasing temp order.
 New higher temp resolves all waiting smaller temps."
'''

'''
The trigger to recognize monotonic stack problems:
"Find next greater/smaller element"
"How long until something larger/smaller"
"Largest rectangle" 
"Trapping rain water"

Any problem where:
→ you need to find something ahead
→ and elements "wait" until they find their answer
→ = monotonic stack
'''