## INTUITION:

1. we would need to preserve the order
2. it will be some form of traversal
3. BRUTE --> finding sum of every subarray using 3 nested loops --> O(n^3)
4. BETTER --> finding sum of every subarray using running sum --> O(n^2)

## Lets start with the OPTIMAL --> which is Kadane's Algorithm

```
1. if the curr_sum is -ve --> restart your sum to zero and move ahead
2. if the curr sum is +ve --> kepe it and move ahead
```

### CODE

```cpp
class Solution {
public:
    int maxSubArray(vector<int>& nums) {

        int global_max = INT_MIN;
        int n = nums.size();
        int curr_sum = 0;

        for (int num : nums) {

            curr_sum += num;

            if (curr_sum > global_max) {
                global_max = curr_sum;
            }

            if (curr_sum < 0) {
                curr_sum = 0;
            }
        }

        return global_max;
    }
};
```
