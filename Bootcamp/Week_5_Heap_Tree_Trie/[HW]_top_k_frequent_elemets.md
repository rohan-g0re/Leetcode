Given an integer array nums and an integer k, return the k most frequent elements. You may return the answer in any order.

Example 1:

Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]

Example 2:

Input: nums = [1], k = 1
Output: [1]

****************

## Intuition

- Count frequency of each element
- Get top k most frequent elements
- Can use heap (priority queue) or bucket sort

## BRUTE FORCE --> Sort by Frequency

- Count frequencies
- Sort by frequency
- Return top k

```
class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {
        
        unordered_map<int, int> freq;
        for (int num : nums) {
            freq[num]++;
        }
        
        vector<pair<int, int>> pairs;
        for (auto& p : freq) {
            pairs.push_back({p.second, p.first});
        }
        
        sort(pairs.rbegin(), pairs.rend());
        
        vector<int> result;
        for (int i = 0; i < k; i++) {
            result.push_back(pairs[i].second);
        }
        
        return result;
    }
};
```

TC --> O(n log n) for sorting
SC --> O(n) for frequency map

## OPTIMAL --> Min Heap (Priority Queue)

- Use min heap of size k
- Keep only k most frequent elements
- Heap stores pairs: (frequency, element)

```
class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {
        
        // Count frequencies
        unordered_map<int, int> freq;
        for (int num : nums) {
            freq[num]++;
        }
        
        // Min heap: pair<frequency, element>
        priority_queue<pair<int, int>, vector<pair<int, int>>, greater<pair<int, int>>> minHeap;
        
        for (auto& p : freq) {
            minHeap.push({p.second, p.first});
            
            // Keep only k elements
            if (minHeap.size() > k) {
                minHeap.pop();
            }
        }
        
        // Extract results
        vector<int> result;
        while (!minHeap.empty()) {
            result.push_back(minHeap.top().second);
            minHeap.pop();
        }
        
        return result;
    }
};
```

## ALTERNATIVE --> Bucket Sort

- Create buckets for each frequency
- Elements with frequency i go to bucket[i]
- Traverse buckets from highest to lowest

```
class Solution {
public:
    vector<int> topKFrequent(vector<int>& nums, int k) {
        
        // Count frequencies
        unordered_map<int, int> freq;
        for (int num : nums) {
            freq[num]++;
        }
        
        // Bucket: index = frequency, value = list of elements
        vector<vector<int>> buckets(nums.size() + 1);
        for (auto& p : freq) {
            buckets[p.second].push_back(p.first);
        }
        
        // Extract top k
        vector<int> result;
        for (int i = buckets.size() - 1; i >= 0 && result.size() < k; i--) {
            for (int num : buckets[i]) {
                result.push_back(num);
                if (result.size() == k) break;
            }
        }
        
        return result;
    }
};
```

## TC --> O(n) for bucket sort, O(n log k) for heap approach
## SC --> O(n) for frequency map and buckets/heap

