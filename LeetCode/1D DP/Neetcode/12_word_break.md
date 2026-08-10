## Attempt 1:
BETTER SOLUTION I GUESS --> create all words that can be built --> find if we get ours
--> childish optimizations:
1. starting letter should be same
2. size should match (early termination)


# Attempt 2: --> TLE
- take every letter from string and keep creating a string --> keep matching it with dictionary
- once we find a word --> add it into SOME DATA STUCTURE
- we know that we can only BUILD on top of these

QUEUE OF PROSPECTS
- keep building string -> match every iteration of substring in dict
- if match --> its a prospect --> push into queue


```cpp
class Solution {

public:
    bool wordBreak(string s, vector<string>& wordDict) {

        unordered_set<string> dict (wordDict.begin(), wordDict.end());
        queue <string> q;
        int n = s.size();

        // 1. intially

        int posi = 0;
        string temp = "";

        while(posi < n){
            
            temp.push_back(s[posi]);

            if(dict.find(temp) != dict.end()){
                // push it
                q.push(temp);
            }
            posi++;
        }

        // if queue is empty --> return false

        while(!q.empty()){

            // pop front --> its size gives us the posi

            string prospect = q.front();
            if(prospect == s) return true;
            q.pop();
            int posi = prospect.size(); // we want it to start from the next letter - hence we are not doing size-1

            // we will make same loop here
            string temp = "";
            while(posi < n){

                temp.push_back(s[posi]);

                if(temp == s) return true;

                if(dict.find(temp) != dict.end()){
                    // push it
                    q.push(prospect + temp);
                }
                posi++;
            }
        }

        return false;

    }
};
```


# ACTUAL SOLUTION --> DP from the END

## MAIN INTUITION:
- at every index `i` --> try EVERY word from dict --> does `s` starting at `i` MATCH this word?
- if match --> then answer at `i` depends on answer at `i + word.size()`
- hence we need to know the FUTURE first --> **start from the ending and go backwards**

#### dp[i] = can we break the substring s[i .. n-1] ?

```cpp
class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {

        int n = s.size();

        // dp[i] --> can we break s[i .. end] ?
        vector<bool> dp(n + 1, false); 

        // n+1 because if we reach n+1th index by "PATCHING True" then it means that we have constructed the complete string --> hence we have INITIALIZED last index as true below

        // 1. base case --> empty suffix is always breakable
        dp[n] = true;

        // 2. fill from the END backwards
        for (int i = n - 1; i >= 0; i--) {

            // try EVERY word at this starting position
            for (string& word : wordDict) {

                int len = word.size();

                // word must fit && substring starting at i matches word
                if (i + len <= n && s.substr(i, len) == word) {

                    // MAIN LOGIC --> if suffix AFTER this word is breakable --> then i is breakable
                    if (dp[i + len] == true) {
                        dp[i] = true;
                        break; // found one valid word --> no need to try more
                    }
                }
            }
        }

        // 3. return --> can we break from index 0 ?
        return dp[0];
    }
};
```
