## INTUITION: That we do not need to preserve the order.

1. find first "VAL" from start
2. find first "NON-VAL" from end 
3. swap
4. move 



```cpp

class Solution {
public:
    int removeElement(vector<int>& nums, int val) {

        int l = 0;
        int r = nums.size() - 1;

        while (l <= r){

            if (nums[l] == val && nums[r] != val){
                swap(nums[l], nums[r]);
                l++;
                r--;
                continue;
            }
            else if (nums[l] != val) l++;
            else if (nums[r] == val) r--;

        }

        return l;
        
    }
};

```

# Python Code

## Approach 1:

bring left to culprit
bring right to valid
swap and update both

```python
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        
        left = 0
        right = len(nums) - 1

        while(left <= right):
            while(left <= right and nums[left] != val): left += 1

            while(left <= right and nums[right] == val): right -= 1

            if left < right:
                nums[left], nums[right] = nums[right], nums[left]
                left += 1
                right -= 1

        return left
```
