## INTUITION:

- I know that it is a DP question and can be solved using fibonacci like recursion
- RULE --> if we reach anywhere more than n --> then it is "OUT OF BOUNDS" --> hence answer not accepted

# Version 1: Starting from 0th stair

## Approach 1 --> Plain recursion

- starting from 0th stair - you always have 2 options --> jump 1 stair or 2 stairs

```cpp
class Solution {
private:
    int helper(int stair, int n){

        // 1. base case --> if reached at ending
        if(stair == n) return 1;


        // 2. logic
        // if not there then we need to take 2 steps

        int left = helper(stair + 1, n);
        
        int right = 0;
        if(stair < n - 1){
            right = helper(stair + 2, n); 
        }

        return left + right;
    }

public:
    int climbStairs(int n) {
        helper(0, n);
    }
};
```

## Approach 2 --> Memoization using a DP array

- we should store how many paths we got from a given STAIR till the end.

```cpp
class Solution {
private:
    int helper(int stair, int n, vector<int>& dp){

        // 1. base cases

        // 1.1 if in table
        if(dp[stair] != -1) return dp[stair];
    
        // 1.2 if reached at ending
        if(stair == n) return 1;

    
        // 2. logic
        // if not there then we need to take 2 steps
        int left = helper(stair + 1, n, dp);
    
        int right = 0;
        if(stair < n - 1){
            right = helper(stair + 2, n, dp); 
        }

        // 3. update and return
        dp[stair] = left + right;
        return dp[stair];
    }


public:
    int climbStairs(int n) {

        vector<int> dp (n + 1, -1);
        return helper(0, n, dp);
    }
};
```

## Approach 3: --> Tabulation

```cpp
class Solution {

public:
    int climbStairs(int n) {

        vector<int> dp (n + 1, -1);
        // 1. base cases:
        // 1.1 base case returns
        if (n == 0 || n == 1) return 1;

        // 1.2 pre-fill since these values are base values 

        dp[0] = 1;
        dp[1] = 1;


        // 2. logic
        // if not there then we need to take 2 steps


        for(int i = 1; i <= n; i++){

            // fill the dp[i] using previous dp values
            int left = dp[i-1];
            int right = 0;
            if (i > 1) right = dp[i - 2];

            // update and return
            dp[i] = left + right;

        }

        return dp[n];
    

    }
};
```

## Approach 4 --> Tabulation WITH Space Optimization --> using 2 variables to store last 2 values instead of an array

- dp[i - 1] becomes prev
- dp[i - 2] becomes prev2
- dp[i] becomes curr

```cpp

class Solution {

public:
    int climbStairs(int n) {

        // 1. base cases:
        // 1.1 base case returns
        if (n == 0 || n == 1) return 1;

        // 1.2 pre-fill since these values are base values 

        int prev = 1;
        int prev2 = 1;


        // 2. logic
        // if not there then we need to take 2 steps

        for(int i = 2; i <= n; i++){

            // fill the dp[i] using previous dp values
            int left = prev;
            int right = 0;
            if (i > 1) right = prev2;

            // calculate
            int curr = left + right;

            //updates:
            prev2 = prev;
            prev = curr;


        }
        return prev;
    }
};
```

# Version 2: Starting from Nth stair

## Approach 1 --> Recursion

- consider we start from n and we have to reach 1
  - we can only pick n-1 and n-2 as moves
  - base case 1 if we reach 0 or less than that - it is 0 distance left BUT 1 step (ITSELF)
  - base case 2 - if we reach 1 - it is 1 distance left

```cpp
class Solution {
public:
    int climbStairs(int n) {

        // base case
        if (n <= 0) return 1;
        if (n == 1) return 1;


        // recusrion calls

        int l = climbStairs (n - 1);
        int r = climbStairs (n - 2);

        // returning logic

        return l+r;
   
    }
};
```

#### RESULT

- this results in a TLE because recursion gives an exponential tc --> O ( 2 ^ n )

## Approach 2 --> Memoization using a dp array

```cpp


class Solution {
public:

    int helper(int n, vector<int>& dp) {


        // base case
        if (n == 0) return 1;
        if (n == 1) return 1;

    
        // check in dp
    
        if (dp[n] != -1){
            return dp[n];
        } 


        // recusrion calls

        int l = helper (n - 1, dp);
        int r = helper (n - 2, dp);


        // returning logic
        dp[n] = l+r;

        return dp[n];
    

    }


    int climbStairs(int n) {

        vector <int> dp (n + 1, -1);

        return helper(n, dp);

    }
};
```
