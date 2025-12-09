#### ELIMINATION IS THE KEY 



```cpp

class Solution {
public:
    int search(vector<int>& nums, int target) {

        int low = 0;
        int high = nums.size() - 1;

        while (low <= high){

            int mid = (low + high) / 2;

            if (nums[mid] == target) return mid;

            // now we need to check which part is sorted so we can make the shrinking likewise

            // 1. check if left part is sorted 
            
            if (nums[low] <= nums[mid]){

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

        return -1;
        
    }
};

```


TC ---> O ( log n )