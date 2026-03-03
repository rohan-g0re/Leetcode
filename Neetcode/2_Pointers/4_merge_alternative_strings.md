
## Approach 1: Single While loop

```cpp
class Solution {
public:
    string mergeAlternately(string word1, string word2) {

        int m = word1.size() - 1;
        int n = word2.size() - 1;
        int p1 = 0;
        int p2 = 0;

        string result = "";

        while (p1 <= m || p2 <= n){

            // append word1
            if (p1 <= m){
                result.push_back(word1[p1]);
                p1++;
            }

            // append word2
            if (p2 <= n){
                result.push_back(word2[p2]);
                p2++;
            }

        }

        return result;
        
    }
};
```


## Approach 2: 2 while loops

```cpp

class Solution {
public:
    string mergeAlternately(string word1, string word2) {
        int m = word1.size();
        int n = word2.size();
        int p1 = 0, p2 = 0;
        string result = "";

        // Main loop: runs only while BOTH strings have characters left
        while (p1 < m && p2 < n) {
            result.push_back(word1[p1++]);
            result.push_back(word2[p2++]);
        }

        // Leftover loop for word1
        while (p1 < m) {
            result.push_back(word1[p1++]);
        }

        // Leftover loop for word2
        while (p2 < n) {
            result.push_back(word2[p2++]);
        }

        return result;
    }
};

```