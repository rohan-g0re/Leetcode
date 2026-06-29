# LC 1967 - Easy


## INTUITION:
1. all substrings needed
2. freq map is not enough --> since we need to have the order of letters as well

### BRUTE --> store all substrings in map --> if match found then pass
- generate substrings using for loop


```cpp
class Solution {
public:
    int numOfStrings(vector<string>& patterns, string word) {

        set<string> st;

        for(int i = 0; i < word.size(); i++){
            string temp = "";
            for(int j = i; j < word.size(); j++){
                // 1. append letter
                temp.push_back(word[j]);

                // 2. add it to set
                st.insert(temp);
            }
        }  

        int result = 0;

        for(string p : patterns){
            // 1. find
            auto it = find(st.begin(), st.end(), p);
            // 2. if not then continue else increment
            if(it != st.end()) result++;
        }

        return result;
    }
};
```


## BETTER: No set required --> Directly use the find function

```cpp
class Solution {
public:
    int numOfStrings(vector<string>& patterns, string word) {

        int result = 0;
        for(string p : patterns){
            if(word.find(p) != string::npos) result++;
        }
        return result;
    }
};
```