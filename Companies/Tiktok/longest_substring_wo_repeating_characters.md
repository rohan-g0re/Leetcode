# LC 3 - Medium

## Intuition: "SUBSTRING WITHOUT REPEATING" --> valid window where every char is unique

- expand r --> include new char
- if s[r] already in CURRENT window --> jump l past its last index
- window data needs to stay IN MEMORY --> map of <char, last_index>

#### IMPORTANT MENTAL FRAMEWORK --> sliding window means DATA ABOUT WINDOW NEEDS TO BE IN MEMORY --> which means we need a DS

### Algo:

```bash
1. initializing:
    1.1 l and r = 0 --> substring under consideration is between L and R (included)
    1.2 hashmap <char, int> --> <alphabet, last_index_where_it_was_found>

2. Start moving r

    2.1 If s[r] not in map OR last index is OUTSIDE current window (mp[s[r]] < l):
        - update map <char, index>
      
    2.2 If s[r] ALREADY in map AND in window (mp[s[r]] >= l):
        - update l = mp[s[r]] + 1 --> so current range no longer has that char
        - update INDEX in map for that char

    2.3 always: update max_length = r - l + 1, then r++
```

### CODE:

```cpp
/*
BASIC --> sliding window --> string in between l and r is our string
- as we need the last location of the character who we just encountered, we need to keep a map such that it stores the character and its last location
*/

class Solution {
public:
    int lengthOfLongestSubstring(string s) {

        // 1. map of char and int
        unordered_map<char, int> mp;
    
        int l = 0;
        int r = 0;
        int n = s.size();
        int max_length = 0;

        while (r < n){

            // case 1: if letter not in map --> add in map
            // case 2: if letter in map BUT OUTSIDE window  --> update in map

            if (mp.find(s[r]) == mp.end() || mp[s[r]] < l ){       // handling case 1 && 2
                mp[s[r]] = r;
            }

            // case 3: if letter in map && in window --> update l, update in map
            else if(mp[s[r]] >= l){
                l = mp[s[r]] + 1;
                mp[s[r]] = r;
            }


            // basics --> update max length, increment r
            max_length = max(max_length, r - l + 1);
            r++;

        }
        return max_length;    
    }
};
```
