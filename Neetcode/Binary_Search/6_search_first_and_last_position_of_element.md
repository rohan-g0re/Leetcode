## LOWER BOUND AND UPPER BOUND IN ACTION


```cpp

class Solution {

private: 

int lowerbound(vector<int>& nums, int target){

    int low = 0;
    int high = nums.size() - 1;
    int ans = nums.size();

    while (low <= high){
        int mid = low + (high - low) / 2;

        if (nums[mid] >= target) {
            ans = mid;
            high = mid - 1;
        }
        else{
            low = mid + 1;
        }
    }
    return ans;
}

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


public:
    vector<int> searchRange(vector<int>& nums, int target) {

        
        int low = lowerbound (nums, target);
        int high = upperbound (nums, target);

        
            // elements ABSENT --> so we should check index first --> checking by access might F*CK it up 

        if(low >= nums.size() || nums[low] != target){
            return {-1, -1};
        }
            
            // elements ACTUALLY present

        else{
            return {low, high - 1};
        }
        
    }
};

```