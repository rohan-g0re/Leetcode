## Approach --> DP with 2D memoization

#### INTUITIONS

1. i need to start from zero --> towards n
2. pick and not pick logic
3. "pick" when valid wrt previous
4. "not pick" can be done whatsoever (valid or invalid current)
   - bcoz even if its valid then the increase can cancel the upcoming length --> eg: 1, 10, 2, 3, 4, 5 --> picking 10 is valid but it will reduce the length of LIS as it would have been 12345

#### WHAT DOES THE DP TABLE MEAN?

- dp_table[index][prev + 1] = best LIS length we can get starting from `index`, given the last picked index was `prev`
- ROW = current index we are deciding on (pick / not pick)
- COL = previous picked index --> but shifted by +1 because prev can be -1 (no previous yet)
  - prev = -1 --> column 0
  - prev = 0 --> column 1
  - prev = n-1 --> column n
  - THATS WHY we need n+1 columns
- we store max(pick, not_pick) at that state --> so we dont recompute the same (index, prev) again

```cpp


class Solution {

private: 

    int LIS (vector<int>& nums, int index, int prev, vector<vector<int>>& dp_table){

        // 1. base conditions

        if (index == nums.size()){
            return 0;
        }

        // already computed this (index, prev) state
        if (dp_table[index][prev + 1] != -1) return dp_table[index][prev + 1];


        // 2. LOGIC

        // 2.1 pick --> ONLY IF valid wrt prev

        int pick = 0;

        if (prev == -1 || nums[index] > nums[prev]){

            // new prev becomes current index --> because we picked it
            pick = 1 + LIS(nums, index+1, index, dp_table);

        }

        // 2.2 not pick whatsoever --> prev stays the same

        int not_pick = 0 + LIS(nums, index+1, prev, dp_table);


        // 3. store + return --> best from this state
        dp_table[index][prev + 1] = max(pick, not_pick);
        return dp_table[index][prev + 1];

    }

public:
    int lengthOfLIS(vector<int>& nums) {

        int n = nums.size();

        // rows = index (0 .. n-1)
        // cols = prev + 1 (prev from -1 .. n-1 --> so n+1 columns)
      
        vector<vector<int>> dp_table (n, vector<int>(n + 1, -1));

        return LIS(nums, 0, -1, dp_table);
      
    }
};
```
