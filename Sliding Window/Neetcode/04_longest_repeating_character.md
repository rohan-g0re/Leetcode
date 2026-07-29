
# MAIN INTUITION --> the window should not have k NON_MAJORITY ELEMENTS

# SLIDING WINDOW LOGIC BOILERPLATE --> so we need a process/data structure which gives us the majority element EACH TIME --> we just need the count COZ indexes will be taken care by l and r --> **therefore the current state of window should be stored IN-MEMORY**


## Approach 1: Sliding Window BRUTE

### ALGORITHM:

```cpp
1. update the count using "r" pointer in DS1  (which gives the current element in window with highest count)
2. If (length of window - freq of top node <= k)
    - yes: nothing --> r++, update max
    - no: remove(increment "l" pointer)

------->>>>> 2 functions needed:
1. DS1:
    - can be heap but each time finding performing "heapify" will be O(n) , but heap DOES NOT HAVE SEARCH
    - can use a simple map but finding top node will take O(n)
    - --> hence lets choose map

2. remove funtion:
    - find s[l] in DS1
    - reduce its count
    - increment l

```

### Code:

```cpp
class Solution {

private:
    int top_freq_node(unordered_map<char, int>& map){
        // goes through map and tells the highest freq a node has

        int maxi = 0;

        for(auto& pair : map){
            if(pair.second > maxi) maxi = pair.second;
        }

        return maxi;
    }

public:
    int characterReplacement(string s, int k) {

        int n = s.size();
        int l = 0;
        int r = 0;
        int max_length = 0;

        //           letter, count
        unordered_map<char, int> map;

        while(r < n){
            
            // 1. update count (SAME SYNTAX even if it is already present or not)
            map[s[r]]++;


            // 2. check validity
            
            if( (r-l+1) - top_freq_node(map) <= k){
                r++;
                max_length = max(max_length, r-l); // generally this is r-l+1 --> but we have ALREADY INCREMENTED r so NO NEED of +1
            }
            else{
                // we need to move left pointer untill we get a valid window
                while ((r-l+1) - top_freq_node(map) > k){
                    map[s[l]]--;
                    l++;
                }
                r++;
            }
        }

        return max_length;
        
    }
};

```


## Approach 2: Sliding Window: Better (Elimiates O(n) map traversal)

### Intuition

We try to make a valid window where all characters become the same, but instead of checking every substring, we fix a target character `c` and ask:

"How long can the window be if we want the entire window to become `c` using at most `k` replacements?"

We slide a window across the string and count how many characters inside it already match `c`.
If the number of characters that **don't match** `c` is more than `k`, the window is invalid, so we shrink it from the left.
By doing this for every possible character, we find the longest valid window.

This idea is simple and beginner-friendly because we only track:

- how many characters match `c`
- how many replacements are needed

### Algorithm

1. Put all unique characters of the string into a set `charSet`.
2. For each character `c` in `charSet`:
   - Set `l = 0` and `count = 0` (count of `c` inside the window).
   - Slide the right pointer `r` across the string:
     - Increase `count` when `s[r] == c`.
     - If the window needs more than `k` replacements, move `l` forward and adjust `count`.
     - Update `res` with the current valid window size.
3. Return the maximum window size found.



### Code:

```cpp

class Solution {
public:
    int characterReplacement(std::string s, int k) {
        int res = 0;
        unordered_set<char> charSet(s.begin(), s.end());

        for (char c : charSet) {
            int count = 0, l = 0;
            for (int r = 0; r < s.size(); r++) {
                if (s[r] == c) {
                    count++;
                }

                while ((r - l + 1) - count > k) {
                    if (s[l] == c) {
                        count--;
                    }
                    l++;
                }

                res = std::max(res, r - l + 1);
            }
        }
        return res;
    }
};

```

## Approach 3: SAME APPROACH as Approach 1, but no map traversal needed

### The Trick: `maxf` Never Decreases

Approach 1 pays **O(26)** per shrink to scan the map and find the current max frequency. Approach 3 avoids that by keeping a single variable `maxf` and **never recalculating** it when the window shrinks.

**How it works:**

1. **On expand (right pointer):** The only character whose count increases is `s[r]`. So the only candidate for a new max is that character. Update with:
   ```cpp
   maxf = max(maxf, count[s[r]]);
   ```
   No map scan needed.

2. **On shrink (left pointer):** When we remove `s[l]`, its count decreases. That character might have been the max, so the *actual* max in the window could go down. But we **do not** update `maxf`. It can become "stale" (higher than the real max in the current window).

3. **Why we don't need to fix it:** 
    - For a substring to be valid, we need window_length - maxf <= k. Here, maxf is the frequency of the most common character in the current window. The difference window_length - maxf tells us how many characters we'd need to change to make the whole window the same character.
    - The biggest valid substring we can get is of size maxf + k. So, the larger maxf is, the better. If maxf doesn't change or goes down, our potential best answer doesn't change. We don't need to update maxf in this case.
    - On the other hand, if maxf goes up, it means we've found a character in the current window that appears more often than in previous windows. This means we might be able to get a longer valid substring, so we update maxf.



4. **Complexity:** O(n) instead of O(26n), because we never scan the map.

### Code:
```cpp
class Solution {
public:
    int characterReplacement(std::string s, int k) {
        unordered_map<char, int> count;
        int res = 0;

        int l = 0, maxf = 0;
        for (int r = 0; r < s.size(); r++) {
            count[s[r]]++;
            maxf = max(maxf, count[s[r]]);

            while ((r - l + 1) - maxf > k) {
                count[s[l]]--;
                l++;
            }
            res = max(res, r - l + 1);
        }

        return res;
    }
};
```