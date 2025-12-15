On day 1, one person discovers a secret.

You are given an integer delay, meaning that each person will share the secret with a new person every day, starting from delay days after discovering the secret. You are also given an integer forget, meaning that each person will forget the secret forget days after discovering it. A person cannot share the secret on the same day they forget it, but they can share it on any day before.

Given an integer n, return the number of people who know the secret at the end of day n. Since the answer may be very large, return it modulo 10^9 + 7.

Example 1:

Input: n = 6, delay = 2, forget = 4
Output: 5
Explanation:
Day 1: Suppose the first person is named A. (1 person)
Day 2: A is the only person who knows the secret.
Day 3: A shares the secret with a new person, B. (2 people)
Day 4: A shares the secret with a new person, C. B shares the secret with a new person, D. (4 people)
Day 5: A forgets the secret. B shares the secret with a new person, E. C shares the secret with a new person, F. (5 people)
Day 6: B forgets the secret. C shares the secret with a new person, G. D shares the secret with a new person, H. (5 people)

Example 2:

Input: n = 4, delay = 1, forget = 3
Output: 6
Explanation:
Day 1: The first person is named A. (1 person)
Day 2: A shares the secret with B. (2 people)
Day 3: A shares the secret with C. B shares the secret with D. (4 people)
Day 4: A forgets the secret. B shares the secret with E. C shares the secret with F. D shares the secret with G. (6 people)

****************

## Intuition

- Track how many people know the secret each day
- People start sharing after `delay` days
- People forget after `forget` days
- Use dynamic programming: dp[i] = number of people who know secret on day i

## BRUTE FORCE --> Track Each Person

- Simulate each person's lifecycle
- Track when they learned, when they start sharing, when they forget

## OPTIMAL --> Dynamic Programming

- dp[i] = number of people who know secret on day i
- For each day i, count:
  - People who learned on day i - forget (they forget today)
  - People who learned on day i - delay (they start sharing today)
- Sum all people who learned between day (i - forget + 1) and day i

```
class Solution {
public:
    int peopleAwareOfSecret(int n, int delay, int forget) {
        
        const int MOD = 1000000007;
        vector<long long> dp(n + 1, 0);
        
        // Day 1: one person knows the secret
        dp[1] = 1;
        
        for (int i = 2; i <= n; i++) {
            // People who can share today: learned between (i - forget + 1) and (i - delay)
            long long canShare = 0;
            
            for (int j = max(1, i - forget + 1); j <= i - delay; j++) {
                canShare = (canShare + dp[j]) % MOD;
            }
            
            // New people who learn today
            dp[i] = canShare;
        }
        
        // Count people who still know secret on day n
        long long result = 0;
        for (int i = max(1, n - forget + 1); i <= n; i++) {
            result = (result + dp[i]) % MOD;
        }
        
        return result;
    }
};
```

## OPTIMIZED --> Prefix Sum Optimization

- Use prefix sum to avoid inner loop
- share[i] = number of people who can share on day i
- dp[i] = number of people who learn on day i

```
class Solution {
public:
    int peopleAwareOfSecret(int n, int delay, int forget) {
        
        const int MOD = 1000000007;
        vector<long long> dp(n + 1, 0);
        vector<long long> share(n + 1, 0);
        
        // Day 1: one person knows
        dp[1] = 1;
        if (1 + delay <= n) {
            share[1 + delay] = 1;
        }
        if (1 + forget <= n) {
            share[1 + forget] = (share[1 + forget] - 1 + MOD) % MOD;
        }
        
        long long currentShare = 0;
        
        for (int i = 2; i <= n; i++) {
            // Update current share count
            currentShare = (currentShare + share[i]) % MOD;
            
            // People who learn today
            dp[i] = currentShare;
            
            // They will start sharing after delay days
            if (i + delay <= n) {
                share[i + delay] = (share[i + delay] + currentShare) % MOD;
            }
            
            // They will forget after forget days
            if (i + forget <= n) {
                share[i + forget] = (share[i + forget] - currentShare + MOD) % MOD;
            }
        }
        
        // Sum all people who still know secret
        long long result = 0;
        for (int i = max(1, n - forget + 1); i <= n; i++) {
            result = (result + dp[i]) % MOD;
        }
        
        return result;
    }
};
```

## TC --> O(n) where n is number of days
## SC --> O(n) for dp and share arrays

