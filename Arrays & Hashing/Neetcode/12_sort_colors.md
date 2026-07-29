# DUTCH NATIONAL FLAG Algorithm

Striver --> https://www.youtube.com/watch?v=tp8JIuCXBaU

```cpp
class Solution {
public:
    void sortColors(vector<int>& nums) {

        int low = 0;
        int mid = 0;
        int high = nums.size() - 1;
        
        while (mid <= high) {

            // frist case --> mid has 0

            if (nums[mid] == 0){
                swap (nums[mid], nums[low]);
                low++;
                mid++;
            }

            // second case --> mid has 1

            else if (nums[mid] == 1){
                mid++;
            }

            // third case --> mid has 2

            else{
                swap (nums[mid], nums[high]);
                high--;
            }

        }

    }
};
```