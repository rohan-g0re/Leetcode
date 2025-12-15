Given a non-empty array nums containing only positive integers, find if the array can be partitioned into two subsets such that the sum of elements in both subsets is equal.

Example 1:

Input: nums = [1,5,11,5]
Output: true
Explanation: The array can be partitioned as [1, 5, 5] and [11].

Example 2:

Input: nums = [1,2,3,5]
Output: false
Explanation: The array cannot be partitioned into two equal sum subsets.

****************

## Intuition

- If sum is odd, cannot partition into equal subsets
- If sum is even, need to find subset with sum = total_sum / 2
- This becomes a subset sum problem: can we make sum/2 using some elements?

## BRUTE FORCE --> Recursion

- Try including/excluding each element
- Check if we can make target sum

```
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int sum = 0;
        for (int num : nums) {
            sum += num;
        }
        
        if (sum % 2 != 0) return false;
        
        int target = sum / 2;
        return canMakeSum(nums, 0, target);
    }
    
private:
    bool canMakeSum(vector<int>& nums, int index, int target) {
        if (target == 0) return true;
        if (index >= nums.size() || target < 0) return false;
        
        // Include current element or exclude it
        return canMakeSum(nums, index + 1, target - nums[index]) ||
               canMakeSum(nums, index + 1, target);
    }
};
```

TC --> O(2^n) exponential
SC --> O(n) recursion stack

## OPTIMAL --> Dynamic Programming (0/1 Knapsack)

- dp[i][j] = can we make sum j using first i elements
- dp[i][j] = dp[i-1][j] || dp[i-1][j - nums[i-1]]

```
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        
        int sum = 0;
        for (int num : nums) {
            sum += num;
        }
        
        if (sum % 2 != 0) return false;
        
        int target = sum / 2;
        int n = nums.size();
        
        vector<vector<bool>> dp(n + 1, vector<bool>(target + 1, false));
        
        // Base case: sum 0 is always possible
        for (int i = 0; i <= n; i++) {
            dp[i][0] = true;
        }
        
        for (int i = 1; i <= n; i++) {
            for (int j = 1; j <= target; j++) {
                // Don't include current element
                dp[i][j] = dp[i - 1][j];
                
                // Include current element if possible
                if (j >= nums[i - 1]) {
                    dp[i][j] = dp[i][j] || dp[i - 1][j - nums[i - 1]];
                }
            }
        }
        
        return dp[n][target];
    }
};
```

## OPTIMIZED --> Space Optimized (1D DP)

- Use only 1D array, iterate backwards to avoid overwriting

```
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        
        int sum = 0;
        for (int num : nums) {
            sum += num;
        }
        
        if (sum % 2 != 0) return false;
        
        int target = sum / 2;
        vector<bool> dp(target + 1, false);
        dp[0] = true;  // Base case: sum 0 is always possible
        
        for (int num : nums) {
            // Iterate backwards to avoid using same element twice
            for (int j = target; j >= num; j--) {
                dp[j] = dp[j] || dp[j - num];
            }
        }
        
        return dp[target];
    }
};
```

## TC --> O(n * target) where target = sum/2
## SC --> O(target) for 1D dp, O(n * target) for 2D dp

