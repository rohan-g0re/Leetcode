## INTUITION:

1. traverse until we get a character which is already added in the substring
2. we need to preserve the order of string/characters

## BRUTE:

1. Check every substring and maintain a freq count - and keep updating length count
2. if already there in map
   2.1 break
   2.2 update max
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

# OPTIMAL --> SLIDING WINDOW

#### IMPORTANT MENTAL FRAMEWORK --> as we will need sliding window for this --> this means that the DATA ABOUT WINDOW NEEDS TO BE IN MEMORY --> which means that we need to use a data structure

### Algo:

```bash
1. initializing:
    1.1 l and r pointers to zero --> this means that the SUBSTRING UNDER CONSIDERATION IS BETWEEN L AND R (included)
    1.2 Hashmap which stores <char, int> --> <alphabet, last_index_where_it_was_found>


2. Start moving r

    2.1 If s[r] is not in map:
        - update in map <char, index>
        - calculate length = r - l + 1
        - update global_max if possible

    2.2 If s[r] is ALREADY in map:
        - IMPORTANT --> CHECK IF ITS INDEX IS IN THE CURRENT RANGE OF L AND R --> because it is possible that there is already an element but we dont have it in the current range --> IF ITS NOT then do 2.1

considering it is in range:

        - update the l pointer to map[s[r]] + 1 --> so that we update our current range in such a way that we dont have the element anymore
        - update INDEX in map for that element 
        - calc length 
        - update global_max if possible
```

### CODE:

```cpp
/*
BASIC --> sloding window --> string in between l and r is our string
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
            // case 2: if letter in map BUT not in window  --> update in map

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