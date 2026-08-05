# Longest Palindromic Subsequence

## Approach MAIN --> **LCS with reversed string**

#### MAIN INTUITION
- a palindrome reads the same forwards and backwards
- so LPS of `s` = **LCS of `s` and `reverse(s)`**
- reuse the LCS tabulation template directly

#### WHAT DOES THE DP TABLE MEAN?
- same as LCS --> `dp_table[i][j]` = LCS of first `i` chars of `s` and first `j` chars of `reverse(s)`
- size = `(m+1) x (n+1)` --> index shifted by +1
- already initialized with 0s --> **no need for base-case loops** (row 0 / col 0 = empty string)

```cpp
class Solution {

private: 
    int LCS(string text1, string text2) {
      
        int m = text1.size();
        int n = text2.size();

        // already all 0s --> base case done
        vector<vector<int>> dp_table (m + 1, vector<int>(n + 1, 0));

        for (int index1 = 1; index1 < m + 1; index1++){          
            for (int index2 = 1; index2 < n + 1; index2++){

                // MATCH --> take both chars
                if (text1[index1 - 1] == text2[index2 - 1]){          
                    dp_table[index1][index2] = 1 + dp_table[index1 - 1][index2 - 1];
                }

                // NOT MATCH --> shift one side, take max
                else{
                   dp_table[index1][index2] = 0 + max(dp_table[index1 - 1][index2], 
                                            dp_table[index1][index2 - 1]);
                }
            }
        }
        return dp_table[m][n];
    }

public:
    int longestPalindromeSubseq(string s) {

        // reverse s --> now LPS becomes LCS(s, reverse)
        string r = s;
        reverse(r.begin(), r.end());

        return LCS(s, r);
    }
};
```
