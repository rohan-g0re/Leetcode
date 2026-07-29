# C++ Comparisions are not CHAIN-ABLE 

### Hence we cant write: nums[low] == nums[mid] == nums[high]

```cpp

class Solution {
public:
    bool search(vector<int>& nums, int target) {
        
        int low = 0;
        int high = nums.size() - 1;

        while (low <= high){

            int mid = (low + high) / 2;

            if (nums[mid] == target) return true;


            // extra crazy edge case handling 

            if (nums[low] == nums[mid] && nums[mid] == nums[high]){
                low += 1;
                high -= 1;
                continue;
            }

            // now we need to check which part is sorted so we can make the shrinking likewise

            // 1. check if left part is sorted 
            
            else if (nums[low] <= nums[mid]){

                // if sorted then does target lie in range

                if (nums[low] <= target && target  <= nums[mid]){
                    high = mid - 1;
                }
                
                // we fucked up - go into the other part
                else{
                    low = mid + 1;
                }

            }
            // right is sorted
            else{
                
                if (nums[mid] <= target && target  <= nums[high]){
                    low = mid + 1;
                }
                // we fucked up - go into the other part
                else{
                    high = mid - 1;
                }

            }
        }

        return false;

    }
};

```