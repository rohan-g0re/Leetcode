```
Previously we verified anagrams by:
 1. Checking Length and if equal --> check occurence of each and every character
    for this --> checking char count ---> can be done using map (without sorting) or sorting both strings --> simple iterator on both strings 
```


## INTUITION:
1. As we have to return the anagrams - we need to preserve the order - HENCE we cant sort
- BRUTE --> Compare every string with every other string
    
## Solution --> Build a map for sorted words

1. maintain a map that has 
2. key --> sorted word  |   value --> vector of all the ACTUAL words (chain)


```cpp
class Solution {
public:
    vector<vector<string>> groupAnagrams(vector<string>& strs) {

        unordered_map <string, vector<string>> map;

        for (auto& string_i : strs){
            string sortedkey = string_i;
            sort(sortedkey.begin(), sortedkey.end());
            
            // this will make thekey value pair as (aet, ate)
            map[sortedkey].push_back(string_i);

        }

        // now we insert all the chains in the result vector 

        vector <vector<string>> result;

        for (auto& pair : map){

            result.push_back(pair.second);

        }

        return result;

    }
};
```