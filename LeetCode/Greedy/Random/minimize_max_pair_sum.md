# Leetcode 1877 - Medium - POTD 22nd June 2026 



## INTUITION:
1. the higher the number - the greater should be the nerf - the lower should be the partner
2. sort
3. 2 pointers --> one at each end --> that will be our pair
4. calculate for all pairs

### NOTE: Assuming that after sorting, the sum of the last element and the first element will be maximum is WRONG.


## C++ Code:

```cpp

class Solution {
public:
    int minPairSum(vector<int>& nums) {

        sort(nums.begin(), nums.end());
        int l = 0;
        int r = nums.size() - 1;
        int result = INT_MIN;

        while(l < r){
            int sum = nums[l] + nums[r];
            result = max(result, sum);

            l++;
            r--;
        }

        return result;
        
    }
};

```

## Python Code:

```python
class Solution:
    def minPairSum(self, nums: List[int]) -> int:
        
        nums.sort()

        l = 0
        r = len(nums) - 1
        result = 0


        while(l < r):
            result = max(result, nums[l] + nums[r])

            l += 1
            r -= 1

        return result

```