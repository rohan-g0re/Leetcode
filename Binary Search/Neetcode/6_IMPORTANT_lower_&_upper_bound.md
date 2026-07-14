## LOWER BOUND --> **"SMALLEST"** index with `value >= target`

- if less than target -> start = mid + 1 --> bcoz it can never be the answer
- if greater than target --> update answer && end = mid - 1 --> bcoz that position can be the answer

#### INTUITION --> start `ans` with hypothetical index --> this is the answer when target > nums[n-1]

```cpp
class Solution {
public:
    int searchInsert(vector<int>& nums, int target) {

        int low = 0;
        int high = nums.size() - 1;

        int ans = nums.size(); // hypothetical last position as ans --> needed when target is greater than all elements in array

        while(low <= high){
            
            int mid = low + (high - low) / 2;

            if(nums[mid] >= target){ // satisfies cond. --> therefor this "MAYBE" the answer
                ans = mid;  // record the MAYBE answer
                high = mid - 1; // change search space for next iteration -- 1
            }
            else{   // it is less than target, hence, violates our condition, therefore not our answer
                low = mid + 1; // change search space for next iteration - 2
            }
        }
        return ans;
    }
};
```
##### NOTE: we are changing search space both the times because the actual answer is recoded in ans



## UPPER BOUND IN ACTION --> **"SMALLEST"** index with `value > target`

```cpp
int upperbound(vector<int>& nums, int target){

    int low = 0;
    int high = nums.size() - 1;
    int ans = nums.size();

    while (low <= high){
        int mid = low + (high - low) / 2;

        if (nums[mid] > target) {
            ans = mid;
            high = mid - 1;
        }
        else{
            low = mid + 1;
        }
    }
    return ans;
}

```