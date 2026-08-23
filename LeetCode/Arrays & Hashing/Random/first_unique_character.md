# LeetCode 387 - Easy - First Unique Character in a String

## INTUITION

1. We need the **first** character that appears exactly once
2. So we need two pieces of info per character: **freq** and **index**

## BETTER --> map of `char → {freq, index}`

1. First pass: bump freq, overwrite index
2. Second pass: walk the map:
   - as the order in map can be anything - hence maintain a lowest_index variable to return

```cpp
class Solution {
public:
    int firstUniqChar(string s) {

        // character : {freq, index}
        unordered_map<char, pair<int, int>> mp;

        for(int i = 0; i < s.size(); i++){
            mp[s[i]].first++;
            mp[s[i]].second = i;
        }

        int lowest_index = INT_MAX;

        for(auto& pair : mp){
            if(pair.second.first == 1) lowest_index = min(lowest_index, pair.second.second);
        }

        if (lowest_index > s.size()) return -1;
        return lowest_index;
      
    }
};
```

## OPTIMAL --> constant array of 26

Same as Valid Anagram — lowercase letters only, so drop the map.

### Fill a 26-slot freq array, then walk the **string** (NOT THE MAP). The first `freq == 1` you hit is already the leftmost unique.

```cpp
class Solution {
public:
    int firstUniqChar(string s) {

        vector<int> freq (26, 0);

        for(char ch : s){
            freq[ch - 'a']++;
        }

        for(int i = 0; i < s.size(); i++){
            if(freq[s[i] - 'a'] == 1) return i;
        }

        return -1;
    }
};
```

### Python Code:

```python
class Solution:
    def firstUniqChar(self, s: str) -> int:
        counts = {}
      
        for ch in s:
            # IN python we cant directly access the element WHICH IS NOT PRESENT - since it throws an error
            # Hence --> use get() for error handling
            counts[ch] = counts.get(ch, 0) + 1 
          
        for i in range (0, len(s)):
            if counts[s[i]] == 1: return i

        return -1
```

**Time:** O(n) — two linear passes - wrt string length
