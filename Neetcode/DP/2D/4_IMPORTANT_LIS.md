## Approach --> DP with 2D memoization

#### INTUITIONS

```

1. i need to start from zero --> towards n 
2. pick and not pick logic
3. pick when valid wrt previous
4. not pick can be done whatsoever (valid or invalid current)
    - bcoz even its valis then the increase can cancel the upcoming lenght --> eg: 1, 10, 2, 3, 4, 5 --> picking 10 is valid but it will reduces the length of LIS as it would have been 12345
     
```



```cpp


class Solution {

private: 

    int LIS (vector<int>& nums, int index, int prev, vector<vector<int>>& dp_table){

        // 1. base conditions

        if (index == nums.size()){
            return 0;
        }

        if (dp_table[index][prev + 1] != -1) return dp_table[index][prev + 1];


        // 2. LOGIC

        // 2.1 valid wrt prev

        int pick = 0;

        if (prev == -1 || nums[index] > nums[prev]){

            pick = 1 + LIS(nums, index+1, index, dp_table);

        }

        // 2.2 not pick whatsoever

        int not_pick = 0 + LIS(nums, index+1, prev, dp_table);


        // 3. return logic
        dp_table[index][prev + 1] = max(pick, not_pick);
        return dp_table[index][prev + 1];

    }

public:
    int lengthOfLIS(vector<int>& nums) {

        int n = nums.size();

        // Column = prev + 1 (prev varies from -1 to n-1, so column varies from 0 to n)
        
        // && THATS WHY we need n+1 columns 

        vector<vector<int>> dp_table (n, vector<int>(n + 1, -1));

        return LIS(nums, 0, -1, dp_table);
        
    }
};

```