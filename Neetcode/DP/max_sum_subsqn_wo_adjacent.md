

## Approach 1: Tabulation

```cpp

class Solution {
  public:

    int findMaxSum(vector<int>& arr) {
        
        int n = arr.size();
        
        vector<int> dp(n, -1);
        
        dp[0] = arr[0];
        
        for (int i = 1; i < n; i++){
            
            int take = arr[i];
            
            if (i > 1){
                take += dp[i-2];
            }
            
            
            int not_take = 0 + dp[i-1];
            
            
            dp[i] = max(take, not_take);

        }
        
        return dp[n-1];
    }
};

```



## Approach 2: Tabulation with space optimization 

```cpp

class Solution {
  public:

    int findMaxSum(vector<int>& arr) {
        
        int n = arr.size();
        
        int prev1 = arr[0];
        int prev2 = 0; // --> if index goes to negative initially 
        // --> depicts base case 2 
        
        // dp[0] = arr[0];
        
        for (int i = 1; i < n; i++){
            
            int take = arr[i];
            
            if (i > 1){
                take += prev2;
            }
            
            
            int not_take = 0 + prev1;
            
            
            int curr = max(take, not_take);
            
            
            // ------
            
            prev2 = prev1;
            prev1 = curr;
            

        }
        
        return prev1;
    }
};

```