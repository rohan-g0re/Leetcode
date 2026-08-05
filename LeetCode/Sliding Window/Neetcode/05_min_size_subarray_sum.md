## Intuition: "SUBARRAY" --> basically means a valid window

- if sum less than target --> keep including r
- if sum greater than target --> keep removing l

 
```cpp


class Solution {
public:
    int minSubArrayLen(int target, vector<int>& nums) {

        int n = nums.size();
        int l = 0;
        int r = 0;
        int curr_sum = 0;
        int len = INT_MAX;

        while(r < n && l < n){

            // add r if valid
            while(r < n && curr_sum < target){
                curr_sum += nums[r];
                r++;
            }

            // if sum is MORE or EQUAL --> then record len --> increment l
            while(l < r && curr_sum >= target){
                len = min(len, r - l); // DONT ADD +1 bcoz we are already incrementing r in the ABOVE LOOP
                curr_sum -= nums[l];
                l++;
            }
        }
        return len == INT_MAX ? 0 : len;
    }
};

```