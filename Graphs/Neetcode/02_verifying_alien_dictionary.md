
## INTUITION: Make a map so that we can access any letter's index any time without searching the order array.


```cpp
class Solution {
public:
    bool isAlienSorted(vector<string>& words, string order) {
        
        // base case
        if (words.size() == 1) return true;

        // store the order in map
        unordered_map<char, int> mp;

        // fill the map
        for(int i = 0; i < order.size(); i++){
            mp[order[i]] = i;
        }

        // compare words in pairs
        for(int i = 0; i < words.size() - 1; i++){
            string s1 = words[i];
            string s2 = words[i + 1];

            int p = 0;
            int found = false;

            
            while(p < s1.size() && p < s2.size()){
                
                // not a match --> check
                if(s1[p] != s2[p]){

                    // good match 
                    if(mp[s1[p]] < mp[s2[p]]) {
                        found  = true;
                        break;
                    }
                    // bad match
                    else{
                        return false;
                    }
                }

                // else - no match
                p++;
            }

            if(found == false && s1.size() > s2.size()) return false;
        }
        return true;
    }
};
```