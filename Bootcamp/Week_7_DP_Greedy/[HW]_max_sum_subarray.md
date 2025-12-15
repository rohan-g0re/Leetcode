Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.

A subarray is a contiguous part of an array.

Example 1:

Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: [4,-1,2,1] has the largest sum = 6.

Example 2:

Input: nums = [1]
Output: 1

Example 3:

Input: nums = [5,4,-1,7,8]
Output: 23

****************

## Intuition

- Kadane's Algorithm: keep track of maximum sum ending at current position
- If current sum becomes negative, reset it (start new subarray)
- At each position, decide: extend previous subarray or start new one

## BRUTE FORCE --> Check All Subarrays

- Check sum of all possible subarrays
- Keep track of maximum

```
class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        
        int n = nums.size();
        int maxSum = INT_MIN;
        
        for (int i = 0; i < n; i++) {
            int sum = 0;
            for (int j = i; j < n; j++) {
                sum += nums[j];
                maxSum = max(maxSum, sum);
            }
        }
        
        return maxSum;
    }
};
```

TC --> O(n^2)
SC --> O(1)

## OPTIMAL --> Kadane's Algorithm (Dynamic Programming)

- dp[i] = maximum sum of subarray ending at index i
- dp[i] = max(nums[i], dp[i-1] + nums[i])
- Keep track of global maximum

```
class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        
        int n = nums.size();
        int maxEndingHere = nums[0];
        int maxSoFar = nums[0];
        
        for (int i = 1; i < n; i++) {
            // Either extend previous subarray or start new one
            maxEndingHere = max(nums[i], maxEndingHere + nums[i]);
            maxSoFar = max(maxSoFar, maxEndingHere);
        }
        
        return maxSoFar;
    }
};
```

## OPTIMIZED --> Space Optimized

- Don't need to store all dp values, only current and max

```
class Solution {
public:
    int maxSubArray(vector<int>& nums) {
        
        int currentSum = nums[0];
        int maxSum = nums[0];
        
        for (int i = 1; i < nums.size(); i++) {
            currentSum = max(nums[i], currentSum + nums[i]);
            maxSum = max(maxSum, currentSum);
        }
        
        return maxSum;
    }
};
```

## TC --> O(n) where n is length of array
## SC --> O(1) constant space

