## NOTES IN APPLE NOTES

Striver GOD --> https://www.youtube.com/watch?v=JDOXKqF60RQ



```cpp
class Solution {
public:
    void nextPermutation(vector<int>& nums) {


        // step 1: find the brak point --> nad store the "PART 2" index
        int n = nums.size();
        int part2_index = -1;

        for (int i = n-2; i >= 0; i--){
            if (nums[i] < nums[i+1]){
                part2_index = i;
                break;
            }
        }

        /*Comments: 
        1. n-2 because the last number can never be the pivot
        2 if part2_index statys -1, it means that we have the last perm --> the result is going to be sorted array
        */ 

        if (part2_index == -1){

            int l = 0;
            int r = n-1;
            while (l < r){
                swap(nums[l], nums[r]);
                l++;
                r--;
            }

        }
        else{

            // Step 2: find next smallest and swap 

            for (int i = n - 1; i > part2_index; i--){
                if (nums[i] > nums[part2_index]){
                    swap (nums[i], nums[part2_index]);
                    break;
                }
            }

            // Step 3: reversing the "PART 3"
            
            int l = part2_index + 1;
            int r = n-1;
            while (l < r){
                swap(nums[l], nums[r]);
                l++;
                r--;
            }
        }      
    }
};
```