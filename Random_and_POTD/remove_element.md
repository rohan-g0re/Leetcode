### Intuition --> 2 pointers by keeping swapping

### MAINTAIN 2 BLOCKS --> FIRST If eligibility criteria matches for swap - Second, if it does not


```cpp

/*

ELIGIBILITY CRITERIA:

left = val
right = notval

*/


class Solution {
public:
    int removeElement(vector<int>& nums, int val) {
        
        int l = 0;
        int r = nums.size() - 1;

        while(l<=r){
            
            // ELIGIBLE SWAP - SWAP
            if (nums[l] == val && nums[r]!= val){
                swap(nums[l], nums[r]);
                l++;
                r--;
            }

            // NOT ELEGIBLE FOR SWAP
            else{

                if(nums[l] != val) l++; // L not eligible
                
                if(nums[r] == val) r--; // R not eligible
            
            }
        }
        return l;
    }
};


```