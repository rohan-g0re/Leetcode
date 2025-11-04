## INTUITIONS:
1. can use heap-like structure
2. We need to keep a track of count
3. We can use a map for that
4. ISSUE --> how do we return top k from map (thats why heap would have been great)


Attempt 1: Counts to MAP --> SORT MAP 
1. Counts -> O(n), O(1) lookups, O(nlogn), O(k) -->  O(nlogn)


## SOLUTION 1: Freq map --> Heap --> Resultant array 

```cpp
class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {


        // STEP 1 --> Generate the frequency map 

        unordered_map <int, int> map;

        for (int num : nums){
            map[num]++;
        }

        
        priority_queue<pair<int, int>, 
        vector<pair<int, int>>,
        greater<pair<int, int>>
        > min_heap;


        // STEP 2 --> Copy element into heap so that only k remain 

        // we have to copy elements from map to Min-Heap
        // freq should be first in min_heap - bcoz heap compares first value of pair for restrcuturing heap

        for (auto& pair : map){
            
            min_heap.push({pair.second, pair.first});

            if (min_heap.size() > k){
                min_heap.pop();
            }
        }

        // STEP 3: Copy only numbers(not frequencies) from the heap into a results array

        vector <int> result;

        while (!min_heap.empty()){
            result.push_back(min_heap.top().second);
            min_heap.pop();
        }

        return result;


    }
};
```

#### Time & Space Complexity
- Time complexity: O(nlog⁡k)
- Space complexity: O(n+k)
Where n is the length of the array and k is the number of top frequent elements.




## Solution 2 --> Using bucket Sort 

```
- Instead of a heap, create a vector of vector
    - the inner vector @ ith posi. represents that:
        "ALL the elements in inner vector have the frequency of i"
```

```cpp
class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {
        unordered_map<int, int> count;
        vector<vector<int>> freq(nums.size() + 1);

        for (int n : nums) {
            count[n] = 1 + count[n];
        }

        
        
        
        // ----------- IMPORTANT LOGIC ----------- 
        for (const auto& entry : count) {
            freq[entry.second].push_back(entry.first);
        }





        vector<int> res;
        for (int i = freq.size() - 1; i > 0; --i) {
            for (int n : freq[i]) {
                res.push_back(n);
                if (res.size() == k) {
                    return res;
                }
            }
        }
        return res;
    }
};
```
#### Time & Space Complexity
- Time complexity: O(n)
- Space complexity: O(n)