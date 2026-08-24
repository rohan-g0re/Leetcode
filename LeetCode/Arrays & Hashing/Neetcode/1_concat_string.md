# INTUITION:

```cpp

class Solution {
public:
    vector<int> getConcatenation(vector<int>& nums) {

        int n = nums.size();

        vector<int> result (2 * n, -1);

        for (int i = 0; i < n; i++){
            result[i] = nums[i];
            result[i + n] = nums[i];
        }

        return result;
      
    }
};
```

# Python Code

```python
class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:
        nums.extend(nums)
        return nums
```

```python
class Solution:
    def getConcatenation(self, nums: List[int]) -> List[int]:
        return nums + nums
```
