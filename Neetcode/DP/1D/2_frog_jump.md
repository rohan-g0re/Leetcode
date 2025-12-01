## Approach 1: Pure Recursion

```cpp
class Solution {
  public:
  
    int helper (vector<int>& height, int n){
        
        // base case
        if (n == 0) return 0;
        
        if (n == 1) return abs(height[1]-height[0]);
        // can add this base case after dp lookup becasue this will lead to calculating height[1] everytime, instead of looking it up in the dp      
        // also i dont think that we add it in dp table, innit?
        
        
        // recursive calls
        
        int left = helper(height, n-1) + abs(height[n] - height[n-1]);
        
        
        int right = helper(height, n-2) + abs(height[n] - height[n-2]);          
    
        
        
        // return logic
        
        return min(left, right);
        
    }
      
    int minCost(vector<int>& height) {
        
        int n = height.size();
        
        return helper(height, n-1);
    }
};
```
#### RESULT --> TLE 

## Approach 2: recursion turned to memoization

```cpp
class Solution {
  public:
  
    int helper (vector<int>& height, vector<int>& dp, int n){
        
        // base case
        if (n == 0) return 0;
        
        if (n == 1) return abs(height[1]-height[0]);
        // can add this base case after dp lookup becasue this will lead to calculating height[1] everytime, instead of looking it up in the dp      
        // also i dont think that we add it in dp table, innit?


        // check if already done 
        
        if (dp[n] != -1){
            return dp[n];
        }
        
                
        
        // recursive calls
        
        int left = helper(height, dp, n-1) + abs(height[n] - height[n-1]);
        
        
        int right = helper(height, dp, n-2) + abs(height[n] - height[n-2]);          
    
        
        
        // return logic
        
        dp[n] = min(left, right);
        
        return dp[n];
        
    }
      
    int minCost(vector<int>& height) {
        
        int n = height.size();
        
        vector<int> dp (n, -1);
        
        return helper(height, dp, n-1);
        
        
    }
};
```


## Approach 3: Turn memoization to tabulation


```cpp
class Solution {
  public:
  
      
    int minCost(vector<int>& height) {
        
        int n = height.size();
        
        vector<int> dp (n, -1);
        dp[0] = 0;
        dp[1] = abs (height[1] - height[0]);
        
        for (int i = 2; i < n; i++){
            
            int left = dp[i-1] + abs(height[i-1] - height[i]);
            int right = dp[i-2] + abs(height[i-2] - height[i]);
            dp[i] = min (left, right);
        }
        
        return dp[n-1];
        
        
    }
};
```



## Approach 4: SPace optimized tabulation 


```cpp

class Solution {
  public:
  
      
    int minCost(vector<int>& height) {
        
        int n = height.size();
        
        if (n == 1) return 0;

        int prev2 = 0;
        int prev1 = abs (height[1] - height[0]);
        
        
        
        int current = 0; 
        
        for (int i = 2; i < n; i++){
            
            int left = prev1+ abs(height[i-1] - height[i]);
            int right = prev2 + abs(height[i-2] - height[i]);
            current = min (left, right);
            
            
            prev2 = prev1;
            
            prev1 = current;
        }
        
        return prev1;

// submitting prev1 bcoz if n==2 --> it does not enter the loop --> and in that case we have anser in prev1
// also for normal cases it does not matter since "prev1 = current" at the end of every loop iteration  
        
    }
};

```
