You are given an array prices where prices[i] is the price of a given stock on the ith day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.


Input: prices = [7,1,5,3,6,4]
Output: 5



****************




## Brute Force --> Nested loop 

Compare every price[i] - with the price[i + 1.. n]

```
class Solution {
public:
    int maxProfit(vector<int>& prices) {

        int n = prices.size();

        int global_max_profit = INT_MIN;

        for (int i = 0; i < n; i++){

            for (int j = i + 1; j < n; j++){
                if ( prices[j] - prices [i] > global_max_profit ){

                    global_max_profit = prices[j] - prices[i];

                }
            }

        }

        if (global_max_profit < 0) return 0;

        return global_max_profit;
        
    }
};

```

## Next approach -> 


- we can see that the DS is linear, 
- we need to make comparisons AGAIN & AGAIN with array elements 
- we can see that the DS provides random access
- we can see that we are currenlty using O(n^2) for brute force

--> THEREFORE we can use a 2 pointer approach:


1. L pointer as BUY 
2. R pointer as SELl
3. If R is lower than L --> we set L to R - as we have found a new lower position where we can buy the stock
4. IF R is greater than L, we just keep on incrementing R to continue to find the max profit
5. In both the cases we need to increment R





```
class Solution {
public:
    int maxProfit(vector<int>& prices) {
        
        int n = prices.size();
        int L = 0;
        int R = 1;
        int maxP = 0;

        while ( R < n ){

            if (prices[L] < prices[R]){
                maxP = max(maxP, prices[R] - prices[L]);
            }
            else{       // R < L

                L = R;
            } 

            R++;

        }

        return maxP;
        
    }
};
```














