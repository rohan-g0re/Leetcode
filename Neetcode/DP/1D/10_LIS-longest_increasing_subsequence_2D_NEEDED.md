## Approach 1: A better recursion 

#### WE have 2 cases --> 1. SKIP whatsoever - 2. PICK ONLY IF VALID

```cpp

class Solution {
public:

    int helper (vector<int>& nums, int index, int prev_index){

        int n = nums.size();
        // base case
        if (index == n){
            return 0;             
        } 


        // LOGIC
        
        // NOT TAKE --> WHAT-SO-EVER 
        
        int not_take = 0 + helper (nums, index + 1, prev_index);

        // TAKE --> ONLY IF VALID 
        
        int take = 0;

        if (prev_index == -1 || nums[prev_index] < nums[index])
        {
            
// --> 3rd param is index because this is the new prev_index now - as we have added it

            take = 1 + helper (nums, index + 1, index);                       
        }
        
        return max (take, not_take);
    }

    int lengthOfLIS(vector<int>& nums) {
        return helper(nums, 0, -1);       
    }
};

```


## Approach 2: UNORTHODOX: bottom up Tabulation with 1D array  --> O(n^2)

### INTUITION / LOGIC / ALGO 

```bash

this is like rod cutting apporach --> but this time it it not just considering i-1

1. we have to consider ONLY those places in dp which have the corresponding actual value less than nums[i] ----->>> so that we are making an INCREASING array 

2. This lookup cannot be done by maintaing a pointer but we need to LOOP AGAIN AND AGAIN on nums[0...i] to do this
--> and then whenever found nums[k] > nums[i] --> we have to check if "ADDING dp[k] MAKES IT LARGER than - JUST dp[i] by itself"

```


```cpp
class Solution {
public:
    int lengthOfLIS(vector<int>& nums) {

        int n = nums.size();

        if (n == 0) return 0;
        if (n == 1) return 1;

        vector <int> dp (n, 1);
        int result = 0;

        for (int i = 1; i < n; i++){

            for (int j = 0; j < i; j++){
                if (nums[j] < nums[i]){
                    int what_j_brings_to_table = dp[j] + 1; // BASIC INCREMENT of the count bcoz we will be adding this element 
                    
                    dp[i] = max (dp[i], what_j_brings_to_table);
                }
            }
            
            result = max (result, dp[i]);

        }

        return result;        
    }
};

```