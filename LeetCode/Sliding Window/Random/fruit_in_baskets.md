# LC 904 - Fruits in Basket

## INTUITION
- need a subarray such as:
    - having 2 unique numbers ONLY
    - frequency should be MAX


- keep a map maybe
- as we move ahead:
    - if new value is already in map then good --> inrement result
    - if new value is NOT in map --> then we need to setup a while loop for decrementing from left

```cpp

class Solution {
public:
    int totalFruit(vector<int>& fruits) {
        int l = 0;
        int r = 0;
        int result = 0;
        int n = fruits.size();
        unordered_map<int, int> mp;

        while(r < n){
            // 1. add the new value to map
            mp[fruits[r]]++;

            // 2. check for valid window --> by checking if the mpa has only 2 numbers
            while(mp.size() > 2){

                // 2.1 decrement l 
                mp[fruits[l]]--;
                
                // 2.2 if decrementing made it zero - then we can erase it from map
                if(mp[fruits[l]] == 0){
                    mp.erase(fruits[l]);
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
    int totalFruit(vector<int>& fruits) {
        int l = 0;
        int r = 0;
        int result = 0;
        int n = fruits.size();
        unordered_map<int, int> mp;

        while(r < n){
            // 1. add the new value to map
            mp[fruits[r]]++;

            // 2. check for valid window --> by checking if the mpa has only 2 numbers
            if(mp.size() > 2){

                // 2.1 decrement l 
                mp[fruits[l]]--;
                
                // 2.2 if decrementing made it zero - then we can erase it from map
                if(mp[fruits[l]] == 0){
                    mp.erase(fruits[l]);
                }
                
                // 2.3 increment l
                l++;
            }

            // update length ONLY IF VALID --> 
            if(mp.size() <= 2) result = max(result, r - l + 1);
            r++;
        }
        return result;
    }
};
```
