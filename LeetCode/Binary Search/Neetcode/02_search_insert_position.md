## INTUITION --> find **lowerbound** --> target <= nums[mid]

- if nums[mid] >= target:
    - this can be the ans --> record
    - then shift left
- if nums[mid] < target: --> we dont want this
    - then shift right 



```cpp
class Solution {
public:
    int searchInsert(vector<int>& nums, int target) {

        int low = 0;
        int high = nums.size() - 1;

        int res = high + 1; // biggest index at which we can insert a number is n+1th index 

        while(low <= high){

            int mid = low + (high - low) / 2;

            if(nums[mid] >= target){
                res = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }
        return res;
    }
};
```