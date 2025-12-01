## INTUITION:
- I know that it is a DP question and can be solved using fibonacci like recursion  
- RULE --> if we reach anywhere more than n --> then it is "OUT OF BOUNDS" --> hence answer not accepted


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



## Approach 3 --> Tabulation WITH Space Optimization --> using 2 variables to store last 2 values instead of an array 

```cpp

class Solution {
public:

    int climbStairs(int n) {

        if (n == 0 || n == 1) return 1;


        // filling out initla values - BASICALLY converting base cases of recursion to table values

        int prev1 = 1;
        int prev2 = 1;

        for (int i = 2; i <= n; i++){
            int curr = prev1 + prev2;
            prev2 = prev1;
            prev1 = curr;
        }

        return prev1;

    }
};

```