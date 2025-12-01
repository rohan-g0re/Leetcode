## Approach --> OPTIMAL --> DP with tabulation with space optimization 

```cpp
class Solution {
public:
    int rob(vector<int>& nums) {

        int n = nums.size();

        int prev1 = nums[0];
        int prev2 = 0;

        for (int i = 1; i < n; i++){

            int rob_that_shit = nums[i];
            
            if (i > 1){
                rob_that_shit += prev2;
            }

            int spare_that_shit = 0 + prev1;

            int bread = max (rob_that_shit, spare_that_shit);

            prev2 = prev1;
            prev1 = bread;

        }

        return prev1;
        
    }
};
```