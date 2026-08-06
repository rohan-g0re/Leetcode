# LC 76 - Hard

## INTUITION:

- need to maintain **FREQUENCY** --> increment during filling --> decrement during exploration
- WINDOW BASICS:
  1. expand until VALID --> until count == size
  2. When valid --> start doing 3 things:
     - record length
     - crunch
     - update map and count(if needed)

### what map values mean after we start:

- `> 0` --> still needed
- `= 0` --> exact
- `< 0` --> extra in window --> easy crunch


---


## CODE:

```cpp
/*
freq_map <char, freq>

expand until count == size
    valid conditions:
        - if positive in map --> update count
        - update in map

crunch when valid
    - record index + len
    - 2 cases --> easy crunch (stays <= 0) || becomes +ve --> INVALID --> count--
*/

class Solution {
public:
    string minWindow(string s, string t) {

        unordered_map<char, int> mp;
        int m = s.size();
        int n = t.size();
        if (n > m) return "";

        // fill map
        for (char c : t){
            mp[c]++;
        }

        // start the loop
        int l = 0;
        int count = 0;
        int index = -1;
        int minlen = INT_MAX;

        for (int r = 0; r < m; r++){

            // 1. expand --> add r into window
            //      - if positive in map --> update count
            //      - update in map
            if (mp[s[r]] > 0){
                // it was PRE-inserted / still needed
                count++;
            }
            mp[s[r]]--;


            // count is valid --> so crunch
            while (count == n){

                /*
                - we are valid so record the starting index and length
                */

                if (r - l + 1 < minlen){
                    minlen = r - l + 1;
                    index = l;
                }

                // 2 cases --> removing such that new freq is -ve/0 && removing such that it might become +ve
                mp[s[l]]++;

                if (mp[s[l]] > 0){
                    // we will be making the string INVALID
                    count--;
                }
                // else --> easy crunch (was EXTRA / still <= 0)

                l++;
            }
        }

        return index == -1 ? "" : s.substr(index, minlen);
    }
};
```
