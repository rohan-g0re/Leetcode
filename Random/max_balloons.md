# Leetcode 1189 - Easy - POTD 21 June 2026

### INTUITION

- make a hash map
- only have keys: b a l o n
- finally divide the freq with counts in a word
- the lowest is the answer 


```cpp
class Solution {
public:
    int maxNumberOfBalloons(string text) {


        unordered_map<char, int> mp = {{'b', 0}, {'a', 0}, {'l', 0}, {'o', 0}, {'n', 0}};

        for(char c : text){
            
            if(c == 'b' ||c == 'a' ||c == 'l' ||c == 'o' || c == 'n') mp[c]++;
        }

        // min is the answer right --> make sure that if any letter is missing then answer becomes zero?

        int result = INT_MAX;

        for(auto& pair: mp){
            if (pair.second == 0) return 0;
            if(pair.first == 'b' || pair.first == 'a' || pair.first == 'n'){
                result = min(result, pair.second);
            }
            else result = min(result, pair.second / 2);
        }

        return result;

        
    }
};
```

```python

class Solution:
    def maxNumberOfBalloons(self, text: str) -> int:
        
        mp = {'b': 0, 'a': 0, 'l': 0, 'o': 0, 'n': 0}

        # 1. fill the map
        for c in text:
            if c in mp:
                mp[c] += 1


        # 2. check for every pair in map

        result = float(inf)

        for key in mp:
            # 2.1 check if absent --> end
            if mp[key] == 0:
                return 0

            # 2.2 dividing logic
            if key == 'l' or key == 'o':
                result = min(result, mp[key] // 2)

            else:
                result = min(result, mp[key])

        return result

```