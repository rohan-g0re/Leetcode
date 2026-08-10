# Target Sum

## Approach 1 --> Pure Recursion

#### MAIN INTUITION
- each number gets a **sign**: `+` or `-`
- at every index --> **2 choices** --> add it OR subtract it
- when we finish the array --> check if `curr_sum == target`

#### THE 2 BRANCHES
1. **PLUS** --> `curr_sum + nums[index]`
2. **SUBTRACT** --> `curr_sum - nums[index]`
- answer = count of ways from both branches

```cpp
class Solution {

private:
    int helper(vector<int>& nums, int& target, int curr_sum, int index){

        // 1. base --> finished array
        if (index > nums.size() - 1){
            if (curr_sum == target) return 1;
            else return 0;
        }

        // 2. LOGIC --> + or -
        int plus = helper(nums, target, curr_sum + nums[index], index + 1);
        int subtract = helper(nums, target, curr_sum - nums[index], index + 1);

        // 3. return --> total ways
        return (plus + subtract);
    }

public:
    int findTargetSumWays(vector<int>& nums, int target) {

        // start from sum 0, index 0
        return helper(nums, target, 0, 0);
    }
};
```
