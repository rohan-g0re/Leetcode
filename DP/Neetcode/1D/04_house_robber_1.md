# **"TAKE - NOT TAKE" strategy on "NON - Continuous SUB-SEQUENCES"**


## Approach --> OPTIMAL --> DP with tabulation with space optimization 

- dp[i - 1] becomes prev1 --> best till previous house
- dp[i - 2] becomes prev2 --> best till house before that
- dp[i] becomes curr / best

```cpp
class Solution {
public:
    int rob(vector<int>& nums) {

        int n = nums.size();

        // 1. base / pre-fill
        // prev1 = best over houses 0..i-1
        // prev2 = best over houses 0..i-2 (empty prefix starts at 0)
        int prev1 = nums[0];
        int prev2 = 0;

        // 2. logic --> for each house: TAKE or NOT TAKE
        for (int i = 1; i < n; i++) {

            // TAKE --> rob this house + best from i-2 (cannot take adjacent)
            int take = nums[i] + prev2;

            // NOT TAKE --> skip this house --> keep best from i-1
            int skip = 0 + prev1;

            int best = max(take, skip);

            // 3. slide the window (space opt updates)
            prev2 = prev1;
            prev1 = best;
        }

        // 4. return --> prev1 is best over entire array
        return prev1;
    }
};
```
