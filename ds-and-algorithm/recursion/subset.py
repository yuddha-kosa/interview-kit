def subset(nums):
    result = []
    path = []
    def backtrack(index):
        if index == len(nums):
            result.append(path[:])
            return
        
        path.append(nums[index])
        backtrack(index+1)
        path.pop()
        backtrack(index+1)

    backtrack(0)
    return result

print(subset([1,2,3]))

'''
Each "include" line is immediately followed by a deeper backtrack call.
Each backtrack call eventually returns to its caller.
Right after it returns -> there's an "undo" line.
Right after undo -> the SAME level tries "skip" with the same index.


backtrack(index=0) path=[]
  include 1 -> path=[1]
    backtrack(index=1) path=[1]
      include 2 -> path=[1, 2]
        backtrack(index=2) path=[1, 2]
          include 3 -> path=[1, 2, 3]
            backtrack(index=3) path=[1, 2, 3]
              BASE CASE -> save [1, 2, 3]        ← 1st subset found
          undo -> path=[1, 2]
          skip 3
            backtrack(index=3) path=[1, 2]
              BASE CASE -> save [1, 2]           ← 2nd subset found
      undo -> path=[1]
      skip 2
        backtrack(index=2) path=[1]
          include 3 -> path=[1, 3]
            backtrack(index=3) path=[1, 3]
              BASE CASE -> save [1, 3]           ← 3rd subset found
          undo -> path=[1]
          skip 3
            backtrack(index=3) path=[1]
              BASE CASE -> save [1]              ← 4th subset found
  undo -> path=[]
  skip 1
    backtrack(index=1) path=[]
      include 2 -> path=[2]
        backtrack(index=2) path=[2]
          include 3 -> path=[2, 3]
            backtrack(index=3) path=[2, 3]
              BASE CASE -> save [2, 3]           ← 5th subset found
          undo -> path=[2]
          skip 3
            backtrack(index=3) path=[2]
              BASE CASE -> save [2]              ← 6th subset found
      undo -> path=[]
      skip 2
        backtrack(index=2) path=[]
          include 3 -> path=[3]
            backtrack(index=3) path=[3]
              BASE CASE -> save [3]              ← 7th subset found
          undo -> path=[]
          skip 3
            backtrack(index=3) path=[]
              BASE CASE -> save []               ← 8th subset found

FINAL RESULT: [[1, 2, 3], [1, 2], [1, 3], [1], [2, 3], [2], [3], []]
'''