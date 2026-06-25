## Recursion

```cpp

class Solution {

private:
    int helper (vector<int>& nums, int& target, int curr_sum, int index){

        // 1. base condition

        if (index > nums.size() - 1){
            if (curr_sum == target) return 1;
            else return 0;
        }


        // 2. LOGIC --> pick not pick

        int plus = helper(nums, target, curr_sum + nums[index], index + 1) ;
      
        int subtract = helper(nums, target, curr_sum - nums[index], index + 1) ;


        // 3. return logic

        return (plus + subtract);

    }


public:
    int findTargetSumWays(vector<int>& nums, int target) {

        return helper(nums, target, 0, 0);

      
    }
};
```