# Anagram --> An anagram is a word or phrase formed by rearranging the letters of a different word or phrase, using all the original letters exactly once.


## INTUITON:
1. Count of letters will be same
2. Dont really need to preserve the original order 
3. Can compare maybe using exor or something like that 


## SOLUTION 1
1. Map and store count of each letter
2. Next iteration on t to "cancel" each count

## BETTER --> ONe pass with increament and decrement count
1. if found in string 1 --> increment 
2. if found in string 2 --> decrement
3. in the end - everything should be 0;

```cpp
class Solution {
public:
    bool isAnagram(string s, string t) {

        if (s.size() != t.size()) return false;
        
        int size = s.size();
        
        int l = 0;
        int r = 0;
        unordered_map <char, int> map;


        for (int i = 0; i < size; i++){
            map[ s [ i ] ] ++;
            map[ t [ i ] ] --;
        }

        for (auto& pair : map){
            if (pair.second != 0){
                return false;
            }
        }

        return true;

    }
};
```



## OPTIMAL --> Using constant sized arrays --> 26 bcoz all letters are lowercase

1. x - 'a' will give the actual alphabet number since it is ascii 
2. **use single inverted commas for characters**

```cpp
class Solution {
public:
    bool isAnagram(string s, string t) {

        if (s.size() != t.size()) return false;
        
        int size = s.size();
        
        int l = 0;
        int r = 0;
        
        vector <int> frequency (26, 0);


        for (char x : s){
            frequency [ x - 'a'] ++ ;
        }
        
        for (char x : t){
            frequency [ x - 'a'] -- ;
        }
        
        for (int count : frequency){
            if (count != 0){
                return false;
            }
        }

        return true;
    }
};
```
