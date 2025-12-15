Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words.

Note that the same word in the dictionary may be reused multiple times in the segmentation.

Example 1:

Input: s = "leetcode", wordDict = ["leet","code"]
Output: true
Explanation: Return true because "leetcode" can be segmented as "leet code".

Example 2:

Input: s = "applepenapple", wordDict = ["apple","pen"]
Output: true
Explanation: Return true because "applepenapple" can be segmented as "apple pen apple".
Note that you are allowed to reuse a dictionary word.

Example 3:

Input: s = "catsandog", wordDict = ["cats","dog","sand","and","cat"]
Output: false

****************

## Intuition

- Check if string can be broken into words from dictionary
- Use dynamic programming: dp[i] = true if s[0..i-1] can be segmented
- For each position, check if any word from dictionary matches ending at that position

## BRUTE FORCE --> Recursion with Memoization

- Try all possible word combinations
- Check if remaining substring can be segmented

```
class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        unordered_set<string> dict(wordDict.begin(), wordDict.end());
        vector<int> memo(s.length(), -1);
        return canBreak(s, 0, dict, memo);
    }
    
private:
    bool canBreak(string& s, int start, unordered_set<string>& dict, vector<int>& memo) {
        if (start == s.length()) return true;
        
        if (memo[start] != -1) {
            return memo[start] == 1;
        }
        
        for (int end = start + 1; end <= s.length(); end++) {
            string word = s.substr(start, end - start);
            if (dict.count(word) && canBreak(s, end, dict, memo)) {
                memo[start] = 1;
                return true;
            }
        }
        
        memo[start] = 0;
        return false;
    }
};
```

TC --> O(2^n) without memoization, O(n^2) with memoization
SC --> O(n) for memoization

## OPTIMAL --> Dynamic Programming (Bottom-Up)

- dp[i] = true if s[0..i-1] can be segmented
- For each position i, check all words in dictionary
- If word matches ending at i, check if dp[i - word.length()] is true

```
class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        
        int n = s.length();
        unordered_set<string> dict(wordDict.begin(), wordDict.end());
        vector<bool> dp(n + 1, false);
        
        // Empty string can always be segmented
        dp[0] = true;
        
        for (int i = 1; i <= n; i++) {
            for (string word : wordDict) {
                int len = word.length();
                
                // Check if word can end at position i
                if (i >= len && dp[i - len]) {
                    string substr = s.substr(i - len, len);
                    if (substr == word) {
                        dp[i] = true;
                        break;  // Found a valid segmentation
                    }
                }
            }
        }
        
        return dp[n];
    }
};
```

## OPTIMIZED --> Early Break

```
class Solution {
public:
    bool wordBreak(string s, vector<string>& wordDict) {
        
        int n = s.length();
        unordered_set<string> dict(wordDict.begin(), wordDict.end());
        vector<bool> dp(n + 1, false);
        
        dp[0] = true;
        
        for (int i = 1; i <= n; i++) {
            for (int j = 0; j < i; j++) {
                if (dp[j]) {
                    string word = s.substr(j, i - j);
                    if (dict.count(word)) {
                        dp[i] = true;
                        break;
                    }
                }
            }
        }
        
        return dp[n];
    }
};
```

## TC --> O(n * m * k) where n = len(s), m = len(wordDict), k = avg word length
## SC --> O(n) for dp array

