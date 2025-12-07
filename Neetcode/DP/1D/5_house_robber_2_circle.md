## Approach 1 --> directly modifying previous version of question

```cpp
class Solution {
public:

    int helper (vector<int>& temp){
      
        int n = temp.size();

        if (n == 0) return 0;
        if (n == 1) return temp[0];

        int prev1 = temp[0];
        int prev2 = 0;

        for (int i = 1; i < n; i++){

            int left = temp[i] + prev2;
            int right = 0 + prev1;

            int curr = max (left, right);

            prev2 = prev1;
            prev1 = curr;

        }
      
        return prev1;
    }

    int rob(vector<int>& nums) {


        int n = nums.size();

        if (n == 0) return 0;
        if (n == 1) return nums[0];


        vector<int> temp1 (nums.begin(), nums.end() - 1);
        vector<int> temp2 (nums.begin() + 1, nums.end());

        int option1 = helper(temp1);
        int option2 = helper(temp2);

        return max(option1, option2);

      
    }
};
```
