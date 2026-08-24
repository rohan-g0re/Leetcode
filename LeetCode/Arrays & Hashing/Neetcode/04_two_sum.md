

## INTUITIONS:
1. We have to return indices so NEED to preserve the order 

## BRUTE --> Compare each number with every other number using 2 nested loops

## BETTER --> We check if diff is in map or not --> thats why we store map as (number, index) so that we can search wrt number (and not index)

#### SYNTAX CHOICE 

```cpp

//When you use map.find(), it returns an iterator, which acts like a pointer. Since it is pointer-like, you must use the arrow operator -> to access the pair's members:

auto it = map.find(diff);
if (it != map.end()) {
    return {it->second, i};  // it is an iterator (pointer-like)
}


// In range-based for loops, you're getting a direct reference to each key-value pair, not an iterator. Direct objects use the dot operator .:

for (auto pair : map) {
    cout << pair.second;  // pair is a direct reference, not an iterator
}
```

## SOLUTION:

```cpp
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {

        unordered_map <int, int> mp;

        for (int i = 0; i < nums.size(); i++){
            int diff = target - nums[i];

            if (mp.find(diff) != mp.end()){
                return {i, mp[diff]};
            }
            mp.insert({nums[i], i});
        }
        return {};
    }
};
```

# Python Code

## Approach 1: Using Map

```python
class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        
        mp = {}

        for i in range (0, len(nums)):
            diff = target - nums[i]

            # instead of checking if mp[diff] is present --> I can jut check whether key is present in map
            if diff in mp:
                return [i, mp[diff]]
            
            # push in map
            mp[nums[i]] = i
```
