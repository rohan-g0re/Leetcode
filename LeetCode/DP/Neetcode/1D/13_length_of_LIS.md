## Approach 1: "Take Not Take"  Recursion

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

this is like rod cutting approach --> but this time it is not just considering i-1

#### WHAT DOES dp[i] MEAN?

- **dp[i] = length of the Longest Increasing Subsequence that ENDS at index i**
- meaning --> nums[i] MUST be the last element of that subsequence
- it is NOT "LIS of the whole prefix 0..i" --> that would be `max(dp[0] .. dp[i])`
- every index starts at `1` --> because the element by itself is always a valid LIS of length 1

#### HOW DO WE FILL dp[i]?

1. loop `j` from `0 .. i-1` --> look at every previous ending
2. we consider ONLY those `j` where `nums[j] < nums[i]` ----->>> so that we are making an INCREASING array
3. This lookup cannot be done by maintaining a pointer --> we need to LOOP AGAIN on `j = 0..i-1`
4. whenever found `nums[j] < nums[i]` --> check if `dp[j] + 1` makes it LARGER than current `dp[i]`
   - `dp[j] + 1` --> take the best LIS ending at `j`, then APPEND nums[i]
   - `dp[i]` --> best we have already found ending at `i`

#### FINAL ANSWER

- since LIS can END at ANY index --> answer = max over the entire dp table

```cpp
class Solution {
public:
    int lengthOfLIS(vector<int>& nums) {

        int n = nums.size();

        if(n == 0) return 0;
        if(n == 1) return 1;

        // dp[i] --> LIS length ENDING at index i (nums[i] is included as last element)
        vector<int> dp(n, 1);
        int result = 1; // at least single element

        for (int i = 1; i < n; i++){

            // build best LIS that ENDS at i --> by trying every previous ending j        
            for(int j = 0; j < i; j++){

                // only valid if strictly increasing
                if (nums[j] < nums[i]){
                    // dp[i]  --> current best ending at i
                    // dp[j] + 1 --> best ending at j, then append nums[i]
                    dp[i] = max(dp[i], dp[j] + 1);
                }
            }

            // LIS can end anywhere --> track global max across all endings
            result = max(result, dp[i]);
        }
        return result;
    
    }
};
```
