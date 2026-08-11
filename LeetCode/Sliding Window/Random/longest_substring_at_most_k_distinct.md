# Longest Substring With At Most K Distinct Characters

## INTUITION
- EXACTLY same as fruits in basket
    - fruits = this problem with K = 2
- need a substring such as:
    - having K unique characters ONLY (at most)
    - length should be MAX


- keep a map maybe
    - as we move ahead:
        - if new value is already in map then good --> increment freq
        - if new value is NOT in map --> then we need to setup a while loop for decrementing from left
            - until map.size() <= k again

```cpp

class Solution {
public:
    int lengthOfLongestSubstringKDistinct(string s, int k) {
        int l = 0;
        int r = 0;
        int result = 0;
        int n = s.size();
        unordered_map<char, int> mp;

        while(r < n){
            // 1. add the new value to map
            mp[s[r]]++;

            // 2. check for valid window --> by checking if the map has at most k characters
            while(mp.size() > k){

                // 2.1 decrement l 
                mp[s[l]]--;
                
                // 2.2 if decrementing made it zero - then we can erase it from map
                if(mp[s[l]] == 0){
                    mp.erase(s[l]);
                }
                
                // 2.3 increment l
                l++;
            }

            // now we have a valid window --> result is basically the length
            result = max(result, r - l + 1);
            r++;
        }
        return result;
    }
};
```


# OPTIMAL --> preserve the window size

- if valid --> update the window size
- if invalid --> just l++



```cpp

class Solution {
public:
    int lengthOfLongestSubstringKDistinct(string s, int k) {
        int l = 0;
        int r = 0;
        int result = 0;
        int n = s.size();
        unordered_map<char, int> mp;

        while(r < n){
            // 1. add the new value to map
            mp[s[r]]++;

            // 2. check for valid window --> by checking if the map has at most k characters
            if(mp.size() > k){

                // 2.1 decrement l 
                mp[s[l]]--;
                
                // 2.2 if decrementing made it zero - then we can erase it from map
                if(mp[s[l]] == 0){
                    mp.erase(s[l]);
                }
                
                // 2.3 increment l
                l++;
            }

            // update length ONLY IF VALID --> 
            if(mp.size() <= k) result = max(result, r - l + 1);
            r++;
        }
        return result;
    }
};
```
