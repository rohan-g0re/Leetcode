```
Previously we verified anagrams by:
 1. Checking Length and if equal check occurence of each and every character
    - checking char count ---> can be donw using map (without sorting) or sorting both strings --> simple iterator on both strings 
```


## INTUITION:
1. As we have to return the anagrams - we need to preserve the order - HENCE we cant sort


# BRUTE --> Compare evry string with every other string
    
## Attempt 1 --> 
1. Directly build the resultant array - also maintain a result_iterator 
2. Push first element in result[1]
3. If ith elemen in strs == 

NOOOO we can t do this as well as we might need to go back in the resultant vector 


## Solution 

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