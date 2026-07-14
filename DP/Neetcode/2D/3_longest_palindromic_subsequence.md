# Approach MAIN: USING LCS with tabulation with reversed string

```cpp
class Solution {

private: 
    int LCS(string text1, string text2) {
      
        int m = text1.size();
        int n = text2.size();

        vector<vector<int>> dp_table (m + 1, vector<int>(n + 1, 0));

        for(int i = 0; i < m; i++){
            dp_table[i][0] = 0;
        }
        for(int i = 0; i < n; i++){
            dp_table[0][i] = 0;
        }

        for (int index1 = 1; index1 < m + 1; index1++){          
            for (int index2 = 1; index2 < n + 1; index2++){

                // MATCH
                if (text1[index1 - 1] == text2[index2 - 1]){          
                    dp_table[index1][index2] = 1 + dp_table[index1 - 1][index2 - 1];
                }

                // NOT MATCH 
                else{
                   dp_table[index1][index2]  = 0 + max (dp_table[index1 - 1][index2] , 
                                            dp_table[index1][index2 - 1]  );
                }
            }
        }
        return dp_table[m][n];
    }


public:
    int longestPalindromeSubseq(string s) {

        string r = s;
        reverse(r.begin(), r.end());

        return LCS (s, r);
      
    }
};
```
