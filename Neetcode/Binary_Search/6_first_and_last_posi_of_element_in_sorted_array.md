## INTUITION: in a healthy case: it will be the `lower_bound` and `upper_bound - 1` of the array

#### NOTE 1: LB can also be `n` if target is > nums[n-1] --> Therefore, check for index
#### NOTE 2: LB can be different than target if target was not found and it was the position at which target would be inserted --> Therefore, check if LB is equal to the target or not.





```cpp
public:
    vector<int> searchRange(vector<int>& nums, int target) {

        
        int low = lowerbound (nums, target);
        int high = upperbound (nums, target);

        
        // if elements ABSENT --> check if in bounds && check if it is target

        if(low >= nums.size() || nums[low] != target){
            return {-1, -1};
        }
            
            // if elements are ACTUALLY present

        else{
            return {low, high - 1};
        }
        
    }
};
```
