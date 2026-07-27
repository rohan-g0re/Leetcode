# **BRACKET SPAWN** recursion on parts of array

## MAIN INTUITION:
- houses are in a CIRCLE --> first and last are ADJACENT --> cannot rob both
- so spawn House Robber 1 on TWO brackets:
  1. rob houses `[0 .. n-2]` --> exclude last
  2. rob houses `[1 .. n-1]` --> exclude first
- answer = max of both options

## Approach 1 --> directly modifying previous version of question

```cpp
class Solution {
public:

    // SAME as House Robber 1 --> TAKE / NOT TAKE with space opt
    int helper (vector<int>& temp){
    
        int n = temp.size();

        // base cases for the subarray
        if (n == 0) return 0;
        if (n == 1) return temp[0];

        // prev1 = best till i-1 , prev2 = best till i-2
        int prev1 = temp[0];
        int prev2 = 0;

        for (int i = 1; i < n; i++){

            // TAKE --> this house + best from i-2
            int left = temp[i] + prev2;

            // NOT TAKE --> keep best from i-1
            int right = 0 + prev1;

            int curr = max (left, right);

            // slide window
            prev2 = prev1;
            prev1 = curr;

        }
    
        return prev1;
    }

    int rob(vector<int>& nums) {


        int n = nums.size();

        // base cases for full circle
        if (n == 0) return 0;
        if (n == 1) return nums[0];


        // BRACKET 1 --> exclude last house
        vector<int> temp1 (nums.begin(), nums.end() - 1);

        // BRACKET 2 --> exclude first house
        vector<int> temp2 (nums.begin() + 1, nums.end());

        // spawn House Robber 1 on both parts
        int option1 = helper(temp1);
        int option2 = helper(temp2);

        return max(option1, option2);
    }
};
```
