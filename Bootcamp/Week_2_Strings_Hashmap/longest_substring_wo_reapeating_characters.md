## INTUITION:

1. traverse until we get a character which is already added in the substring
2. we need to preserve the order of string/characters

## BRUTE:

1. Check every substring and maintain a freq count - and keep updating length count
2. if already there in map
   2.1 break
   2.2 upadte max
   2.3 start again
   -->>> early stopping criteria at (n-global_max ) --> because if we already have a 5 lenght substring then wecant get a better answer at n-3

```cpp

class Solution {
public:
    int lengthOfLongestSubstring(string s) {

        int global_max = 0;
        int n = s.size();

        for (int i = 0; i < n; i++){
          
            unordered_map <char, int> freq_map;
            freq_map[s[i]]++;

            int curr_max = 1;

            for (int j = i+1; j < n; j++){

                if (freq_map[s[j]] == 0){
                    freq_map[s[j]]++;
                    curr_max++;
                }
                else{
                    global_max = max(global_max, curr_max);
                    break;
                }
            }
            global_max = max(global_max, curr_max);
        }

        return global_max;
      
    }
};

```

# OPTIMAL --> 2pointer / sliding window

### Algo:

```
1. initializing:
    1.1 l and r pointers to zero --> this means that the SUBSTRING UNDER CONSIDERATION IS BETWEEN L AND R (included)
    1.2 Hashmap which stores <char, int> --> <alphabet, last_index_where_it_was_found>


2. Start moving r

    2.1 If s[r] is not in map:
        - update in map <char, index>
        - calculate length = r - l + 1
        - update global_max if possible

    2.2 If s[r] is ALREADY in map:
        - IMPORTANT --> CHECK IF ITS INDEX IS IN THE CURRENT RANGE OF L AND R --> becusae it is possible that there is already an element but we dont have it in the current range --> IF ITS NOT then do 2.1

considering it is in range:

        - update the l pointer to map[s[r]] + 1 --> so that we update our current range in such a way that we donr have the element anymore
        - update INDEX in map for that element 
        - calc length 
        - update global_max if possible
```

### CODE:

```cpp
class Solution {
public:
    int lengthOfLongestSubstring(string s) {

        int l = 0;
        int r = 0;
        int n = s.size();

        int global_max = 0;

        unordered_map<char, int> map;

        while (r < n){

            // if in map && in range 

            if (map.find(s[r]) != map.end() ) {
                if (map [ s[r] ] >= l){
                    l = map[s[r]] + 1;
                }
            }

            // if not in the map 

            int curr_length = r - l + 1;
            global_max = max(global_max, curr_length);
          
          
            map [s[r]] = r; // this will update NEVERTHELESS, whether the l was just updated or not --> so no need of writing this with the l update code in nested if  
          

            r++;
        }

        return global_max;

    }
};
```
