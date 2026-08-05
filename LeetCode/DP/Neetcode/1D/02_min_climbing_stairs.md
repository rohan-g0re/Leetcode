## Approach 1 - Pure Recusrion --> TLE

### IMPORTANT LOGIC

- Where did “start at 0 or 1” happen? --> in main, where we spawned two helpers with 0 and 1 as starting point
- helper(1) means --> minimum cost to reach step 1 starting from the ground (can be any starting point - func does not care).


```cpp
class Solution {

private:
    int helper(vector<int>& cost, int posi){
        
        // base case --> reached on top floor
        if(posi >= cost.size())return 0; // since 0 is the cost of platform(that comes after steps)
        

        // mid way somewhere
        int one = cost[posi] + helper(cost, dp, posi + 1);
        int two = cost[posi] + helper(cost, dp, posi + 2);

        // finding minimum right??/
        return dp[posi];
    }

public:
    int minCostClimbingStairs(vector<int>& cost) {

        // spawn 2 versions --> as we have 2 options for starting line 
        return min (helper(cost, 0), helper(cost, 1));

    }
};
```

## Approach 2: Recusion with Memoization

```cpp
class Solution {

private:
    int helper(vector<int>& cost, vector<int>& dp, int posi){
        
        // base case --> reached on top floor
        if(posi >= cost.size())return 0; // since 0 is the cost of platform(that comes after steps)
        // base case --> in dp 
        if(dp[posi] != -1) return dp[posi];

        // mid way somewhere
        int one = cost[posi] + helper(cost, dp, posi + 1);
        int two = cost[posi] + helper(cost, dp, posi + 2);

        // update the answer in dp table
        dp[posi] = min(one, two);
        // finding minimum right??/
        return dp[posi];
    }

public:
    int minCostClimbingStairs(vector<int>& cost) {

        vector<int> dp(cost.size(), -1);

        // spawn 2 versions --> as we have 2 options for starting line 
        return min (helper(cost, dp, 0), helper(cost, dp, 1));

    }
};
```

## Approach 3: DP with tabulation

```cpp

class Solution {

public:
    int minCostClimbingStairs(vector<int>& cost) {

        int n = cost.size();
        vector<int> dp(n, -1);

        dp[0] = cost[0];
        dp[1] = cost[1];

        for(int i = 2; i < n; i++){
            int one = cost[i] + dp[i-1]; // it may have come from '-1'th step
            int two = cost[i] + dp[i-2]; // it may have come from '-2'th step

            dp[i] = min(one, two);
        }

        // THE ONLY STEPS FROM WHICH WE COULD HAVE REACHED THE "PLATFORM" ABOVE 
        int last_step = dp[n-1];
        int second_last_step = dp[n-2]; 

        return min(last_step, second_last_step);


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
        
        // THE ONLY STEPS FROM WHICH WE COULD HAVE REACHED THE "PLATFORM" ABOVE 
        
        int last_step = prev1;
        int second_last_step= prev2;
   
        return min(last_step, second_last_step);
    }
};
```