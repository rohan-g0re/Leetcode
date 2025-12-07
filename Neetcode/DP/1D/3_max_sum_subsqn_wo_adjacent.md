## Approach 1 : Recursion

```cpp
// User function template for C++
class Solution {
  public:

    int helper (int index, vector<int>& arr){
        
        // give me the max sumattained from 0 to index
        
        // STEP 1. base case
                
        if (index == 0) return arr[index];
        
        if (index < 0) return 0; //out of bounds - reached here because we picked index 1 -- and then did n-2
        
        
        // STEP 2: LOGIC & Recurive calls --> PICK & NOT PICK
        
        int pick = arr[index] + helper(index - 2, arr);
        
        int not_pick = 0 + helper(index - 1, arr);
        
        
        // STEP 3: We have to choose the choice of max
        
        return max(pick, not_pick);
        
        
    }
    
    int findMaxSum(vector<int>& arr) {    
        return helper(arr.size()-1, arr);
    }
};
```


## Approach 2: Recursion with memoization

```cpp
// User function template for C++
class Solution {
  public:

    // give me the max sum attained from 0 to index
    int helper (int index, vector<int>& arr, vector<int>& dp ){
        
        
        // STEP 1. base case
        if (index == 0) return arr[index];
        if (index < 0) return 0; //out of bounds - reached here because we picked index 1 -- and then did n-2
        
        
        // STEP 2 : Before calculation, check if we already have that 
        if (dp[index] != 0) return dp[index];
        
        // STEP 3: LOGIC & Recurive calls --> PICK & NOT PICK
        
        int pick = arr[index] + helper(index - 2, arr, dp);
        
        int not_pick = 0 + helper(index - 1, arr, dp);
        
        
        // STEP 4: We have to choose the choice of max and STORE and RETURN it 
        
        dp[index] = max(pick, not_pick);
        
        return dp[index];   
    }
    
    int findMaxSum(vector<int>& arr) {
        vector<int> dp (arr.size());        
        return helper(arr.size()-1, arr, dp);
      
    }
};
```



## Approach 3: Tabulation

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

## Approach 4: Tabulation with space optimization

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
