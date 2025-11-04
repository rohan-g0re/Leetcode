
# BRUTE --> Check every element with another using a nested loop



# BETTER --> Sort and if nums[i] = nums[i-1], return True

```
class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {

        if (nums.size() == 1) return false;

        sort(nums.begin(), nums.end());

        int n = nums.size();
        for (int i = 1; i < n; i++){
            if (nums[i] == nums[i-1]){
                return true;
            }
        }

        return false;
    }
}
```


# Optimal --> Using Unordered Set
- Check every element in Set --> if found then return true
- this works because the insert and lookup in SET costs O(1)


## USING Set 

```
class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {

        unordered_set <int> seen_numbers;

        for (int x : nums){
            if (seen_numbers.find(x) != seen_numbers.end() ) {
                return true;
            }
            seen_numbers.insert(x);
        }
        return false;


        
    }
};
```

## USING Hashmap

```
class Solution {
public:
    bool containsDuplicate(vector<int>& nums) {

        unordered_map <int, bool> seen_numbers;

        for (int x : nums){
            if (seen_numbers.find(x) != seen_numbers.end() ) {
                return true;
            }
            seen_numbers.insert({x, true});
        }

        return false;        
    }
};
```