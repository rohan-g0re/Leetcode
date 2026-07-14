## INTUITION -> The answer is basically subtracting LCS from both the strings. 

```cpp

class Solution {

private:

int LCS (string word1, string word2){

    int m = word1.size();
    int n = word2.size();

    vector<vector <int>> dp_table (m + 1, vector<int>(n + 1, 0));

    for (int index1 = 1; index1 <= m; index1++){
        for (int index2 = 1; index2 <= n; index2++){

            // match

// index - 1 for both indexes --> Because index variable is created for the table, and in the table we are using one-based indexing. But for strings, we will be using zero-based indexing. Hence, we need to -1 from index. 


            if (word1[index1 - 1] == word2[index2 -1]){
                dp_table[index1][index2] = 1 + dp_table[index1 - 1][index2 - 1];
            }

            // not match
            else{
                dp_table[index1][index2] = 0 + max (dp_table[index1 - 1][index2],
                                                        dp_table[index1][index2 - 1]);
            }

        }
    }

    return dp_table[m][n];


}

public:
    int minDistance(string word1, string word2) {

        int common_length = LCS(word1, word2);

        return (word1.size() + word2.size() - (2 * common_length));
        
    }
};

```