

#### The index is basically going to be the lower bound --> bcoz if there is already an element we push it on the same index --> if element is not there, then we insert the index on the next index

```cpp
class Solution {
public:
    int searchInsert(vector<int>& nums, int target) {

        return lower_bound(nums.begin(), nums.end(), target) - nums.begin();
        
    }
};
```