# BETTER --> Using HashMap 

```cpp
class Solution {
public:
    vector<int> majorityElement(vector<int>& nums) {

        unordered_map <int, int> freq_map;

        for (int num : nums){
            freq_map[num]++;
        }

        int threshold = nums.size() / 3;
        vector <int> result; 

        for (auto& pair : freq_map){
            if (pair.second > threshold){
                result.push_back(pair.first);
            }
        }

        return result;

    }
};
```