# Delete Operation for Two Strings

## INTUITION
- answer = delete everything that is **NOT** in the LCS
- from word1 --> delete `word1.size() - LCS`
- from word2 --> delete `word2.size() - LCS`
- total = `word1.size() + word2.size() - 2 * LCS`

#### WHY?
- LCS is the longest stuff we can **KEEP** in both
- everything else must be deleted to make them equal

#### WHAT DOES THE DP TABLE MEAN?
- same LCS table --> `dp_table[i][j]` = LCS of first `i` / first `j` chars
- index shifted by +1 --> char access uses `index - 1`
- already all 0s --> base covered

```cpp
class Solution {

private:
    int LCS(string word1, string word2){

        int m = word1.size();
        int n = word2.size();

        // already all 0s --> base case done
        vector<vector<int>> dp_table (m + 1, vector<int>(n + 1, 0));

        for (int index1 = 1; index1 <= m; index1++){
            for (int index2 = 1; index2 <= n; index2++){

                // MATCH
                // index - 1 --> table is 1-based, strings are 0-based
                if (word1[index1 - 1] == word2[index2 - 1]){
                    dp_table[index1][index2] = 1 + dp_table[index1 - 1][index2 - 1];
                }

                // NOT MATCH
                else{
                    dp_table[index1][index2] = 0 + max(dp_table[index1 - 1][index2],
                                                        dp_table[index1][index2 - 1]);
                }
            }
        }
        return dp_table[m][n];
    }

public:
    int minDistance(string word1, string word2) {

        int common_length = LCS(word1, word2);

        // delete non-LCS chars from BOTH strings
        return (word1.size() + word2.size() - (2 * common_length));
    }
};
```
