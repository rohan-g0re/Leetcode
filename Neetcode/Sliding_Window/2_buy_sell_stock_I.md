## INTUITION:
#### 1. If we see a dip (price less than what we bought at) we BUY at it
#### 2. If we see a hump (price more than what we bought at) we record POTENTIAL profit

### Therefore, our left pointer(l) will always show our buying position, and our right pointer(r) will always show the latest/selling position.

```cpp
class Solution {
public:
    int maxProfit(vector<int>& prices) {

        int n = prices.size();
        int l = 0;
        int r = 1;
        int profit = 0;

        while(r < n){
            if (prices[r] > prices[l]){
                profit = max (profit, prices[r] - prices[l]);
            }
            else{
                l = r;
            }
            r++; // r increments any-which-ways --> unlike l which changes only when we find a dip
        }
        return profit;
    }
};