#### pointer 1 --> pointing to new places to put unique numbers on
#### pointer 2 --> finding next unique number & ignoring duplicates --> Number should not be the same as the previous number and the number the pointer 1 is pointing at. 


```cpp

class Solution {
public:
    int removeDuplicates(vector<int>& nums) {

        int pointer1 = 0;
        int pointer2 = 1;

        int count = 1; // because first element is always unique

        while (pointer2 < nums.size()){
            
            // found duplicate that is already added
            if(nums[pointer2] == nums[pointer2 - 1] && nums[pointer2] == nums[pointer1]){
                pointer2++;
                continue;
            }

            // found unique
            else if (nums[pointer2] != nums[pointer2 - 1] && nums[pointer2] != nums[pointer1]){
                count++;

                pointer1++;
                nums[pointer1] = nums[pointer2];
                pointer2++;
            }
        }

        return count;   
    }
};
```