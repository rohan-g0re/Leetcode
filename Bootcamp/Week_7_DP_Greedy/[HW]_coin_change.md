You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.

You may assume that you have an infinite number of each kind of coin.

Example 1:

Input: coins = [1,2,5], amount = 11
Output: 3
Explanation: 11 = 5 + 5 + 1

Example 2:

Input: coins = [2], amount = 3
Output: -1
Explanation: The amount of 3 cannot be made up with coins of value 2.

Example 3:

Input: coins = [1], amount = 0
Output: 0

****************

## Intuition

- Minimum coins to make amount
- For each amount, try all coins
- dp[i] = minimum coins needed to make amount i
- dp[i] = min(dp[i], dp[i - coin] + 1) for all coins

## BRUTE FORCE --> Recursion

- Try all combinations recursively
- For each amount, try each coin

```
class Solution {
public:
    int coinChange(vector<int>& coins, int amount) {
        if (amount == 0) return 0;
        if (amount < 0) return -1;
        
        int minCoins = INT_MAX;
        for (int coin : coins) {
            int result = coinChange(coins, amount - coin);
            if (result != -1) {
                minCoins = min(minCoins, result + 1);
            }
        }
        
        return minCoins == INT_MAX ? -1 : minCoins;
    }
};
```

TC --> O(amount^coins.length) exponential
SC --> O(amount) recursion stack

## OPTIMAL --> Dynamic Programming (Bottom-Up)

- dp[i] = minimum coins to make amount i
- Initialize dp[0] = 0
- For each amount from 1 to target, try all coins

```
class Solution {
public:
    int coinChange(vector<int>& coins, int amount) {
        
        vector<int> dp(amount + 1, amount + 1);  // Initialize with impossible value
        dp[0] = 0;  // Base case: 0 coins needed for amount 0
        
        for (int i = 1; i <= amount; i++) {
            for (int coin : coins) {
                if (coin <= i) {
                    dp[i] = min(dp[i], dp[i - coin] + 1);
                }
            }
        }
        
        return dp[amount] > amount ? -1 : dp[amount];
    }
};
```

## OPTIMIZED --> Early Termination

```
class Solution {
public:
    int coinChange(vector<int>& coins, int amount) {
        
        if (amount == 0) return 0;
        
        vector<int> dp(amount + 1, INT_MAX);
        dp[0] = 0;
        
        for (int i = 1; i <= amount; i++) {
            for (int coin : coins) {
                if (coin <= i && dp[i - coin] != INT_MAX) {
                    dp[i] = min(dp[i], dp[i - coin] + 1);
                }
            }
        }
        
        return dp[amount] == INT_MAX ? -1 : dp[amount];
    }
};
```

## TC --> O(amount * coins.length)
## SC --> O(amount) for dp array

