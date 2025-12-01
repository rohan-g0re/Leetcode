## Approach 1: Tabulation

### INTUITION

```bash



ROD CUTTING LOGIC --> current best can be either
    1. best of 0->i-1 * i
    2. i itself
but this only works for max_sum_subarray 

FOR PRODUCT --> REMEMBER we need to keep a track of MINIMUM PRODUCT AS WELL because it can anytime turn to positive - if a negative number comes up

Therefore logic becomes like:

CURRENT BEST CAN BE FROM: 
    1. best of max 0->i-1 * i -------- max_prod [i-1] * i
    2. best of min 0->i-1 * i -------- min_prod [i-1] * i 
    3. i itself


```



```cpp


class Solution {
public:
    int maxProduct(vector<int>& nums) {

        int n = nums.size();

        vector<int> max_dp (n);
        vector<int> min_dp (n);

        max_dp[0] = nums[0];
        min_dp[0] = nums[0];

        int global_max = nums[0];
        
        for (int i = 1; i < n; i++){

            // there are 3 candidates: 
            int cand1 = nums[i];
            int cand2 = nums[i] * max_dp[i-1];
            int cand3 = nums[i] * min_dp[i-1];

            // logic to update tables 
            max_dp[i] = max(cand1, max(cand2, cand3));
            min_dp[i] = min(cand1, min(cand2, cand3));
            
            if (max_dp[i] > global_max){
                global_max = max_dp[i];
            }

        }

        return global_max;      
    }
};

```



## Approach 2: Tabulation with Space Optimization 


```cpp

class Solution {
public:
    int maxProduct(vector<int>& nums) {

        int n = nums.size();

        int prev_max_prod = nums[0];
        int prev_min_prod = nums[0];

        int global_max = prev_max_prod;
        
        for (int i = 1; i < n; i++){

            // there are 3 candidates: 
            int cand1 = nums[i];
            int cand2 = nums[i] * prev_max_prod;
            int cand3 = nums[i] * prev_min_prod;

            // logic to update tables 
            int curr_max_prod = max(cand1, max(cand2, cand3));
            int curr_min_prod = min(cand1, min(cand2, cand3));
            
            if (curr_max_prod > global_max){
                global_max = curr_max_prod;
            }

            prev_max_prod = curr_max_prod;
            prev_min_prod = curr_min_prod;
        }
        return global_max;      
    }
};

```