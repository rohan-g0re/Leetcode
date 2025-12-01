


## Approach 1 - Pure Recusrion --> TLE 

### IMPORTANT LOGIC 

```bash

Where did “start at 0 or 1” happen?
Look at what helper(1) and helper(2) actually represent:

    helper(1) means: minimum cost to reach step 1 starting from the ground.

        That implicitly includes the path: “start at step 1 for free, then pay cost the first time you use it”.

    helper(2) means: minimum cost to reach step 2, which includes both:

        via step 1 (which itself came from 0 or start)

        via step 0 directly.

So, because helper(i) recursively considers all ways to reach i, starting from the beginning of the staircase, the logic “start at 0 or 1” is already baked into those helper(i) values.


```


```cpp

class Solution {
public:

    int helper (vector<int>& cost, int n){

        // base cases
        if (n == 0) return cost[0];
        if (n < 0) return 0;

        // logic and recursive calls
        int left = cost[n] + helper (cost, n-1);

        int right = cost[n] + helper (cost, n-2);


        return min (left, right);
    }


    int minCostClimbingStairs(vector<int>& cost) {

        int n = cost.size();

        int from_zero = helper (cost, n-1);
        int from_one = helper (cost, n-2);

        return min (from_zero, from_one);
        
    }
};
```


## Approach 2: Recusion with Memmoization 

```cpp

class Solution {
public:

    int helper (vector<int>& cost, vector<int>& dp, int n){

        // base cases
        if (n == 0) return cost[0];
        if (n < 0) return 0;


        // dp lookup

        if (dp[n] != -1){
            return dp[n];
        }


        // logic and recursive calls
        int left = cost[n] + helper (cost, dp, n-1);

        int right = cost[n] + helper (cost, dp, n-2);

        dp[n] = min (left, right);

        return dp[n];
    }


    int minCostClimbingStairs(vector<int>& cost) {

        int n = cost.size();

        vector <int> dp (n, -1);

        int from_zero = helper (cost, dp, n-1);
        int from_one = helper (cost, dp, n-2);

        return min (from_zero, from_one);
        
    }
};

```



## Approach 3: DP with tabulation


```cpp

class Solution {
public:
    int minCostClimbingStairs(vector<int>& cost) {

        int n = cost.size();

        vector <int> dp (n, -1);

        if (n == 2) return min(cost[0], cost[1]);

        dp[0] = cost[0];
        dp[1] = cost[1];

        for (int i = 2; i < n; i++){

            int left = cost[i] + dp[i-1];
            int right = cost[i] + dp[i-2];

            dp[i] = min (left, right);
        }

        int from_zero = dp[n-1]; // need not do this but did this to REMEMBER that we are dealing with 2 different values
        int from_one = dp[n-2]; // need not do this but did this to REMEMBER that we are dealing with 2 different values
        

        return min(from_zero, from_one);
    }
};


```


## Approach 4: Tabulation with Space optimization 


```cpp


class Solution {
public:
    int minCostClimbingStairs(vector<int>& cost) {

        int n = cost.size();

        int prev2 = cost[0];
        int prev1 = cost[1];

        if (n == 2) return min(prev1, prev2);

        for (int i = 2; i < n; i++){

            int left = cost[i] + prev1;
            int right = cost[i] + prev2;

            int current = min (left, right);

            // -----
            
            prev2 = prev1;
            prev1 = current;
            
        }

        int from_zero = prev1; // need not do this but did this to REMEMBER that we are dealing with 2 different values
        int from_one = prev2; // need not do this but did this to REMEMBER that we are dealing with 2 different values
        

        return min(from_zero, from_one);
    }
};


```