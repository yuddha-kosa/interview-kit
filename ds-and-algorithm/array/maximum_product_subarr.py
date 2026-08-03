class Solution:
    def maxProduct(self, nums):
        
        max_product = nums[0]
        curr_product = nums[0]

        for i in range(1, len(nums)):
            loc_curr = curr_product * nums[i]
            if loc_curr <= curr_product:
                curr_product = nums[i]
            else:
                #curr_product *=  nums[i]
                curr_product = loc_curr
            
            max_product = max(max_product, curr_product)
        return max_product

sol = Solution()
print(sol.maxProduct([2,3,-2,4]))
print(sol.maxProduct([-2,0,-1]))