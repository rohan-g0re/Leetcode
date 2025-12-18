

## naive recursion

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


## Incomplete memoization

```cpp

class Solution {

private:
    int helper (vector<int>& nums, int& target, int curr_sum, int index){

        // 1. base condition

        if (index > nums.size() - 1){
            if (curr_sum == target) return 1;
            else return 0;
        }


        // check in dp_table

        if (dp_table[curr_sum][index] != -1){
            return dp_table[curr_sum][index];
        }




        // 2. LOGIC --> pick not pick

        int plus = helper(nums, target, curr_sum + nums[index], index + 1) ;
        
        int subtract = helper(nums, target, curr_sum - nums[index], index + 1) ;


        // 3. return logic

        return (plus + subtract);

    }


public:
    int findTargetSumWays(vector<int>& nums, int target) {

        int total_sum = 0;
        for(auto num : nums){
            total_sum += num;
        }



        vector<vector<int>> dp_table( 2* total_sum, vector<int>(nums.size(), -1) );



        return helper(nums, target, 0, 0);

        
    }
};

```