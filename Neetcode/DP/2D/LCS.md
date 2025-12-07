## Approach 1 --> Pure Recursion

```cpp

class Solution {

private: 

    int helper (int index1, int index2, string text1, string text2){
      
        // STEP 1: Base cases

        if (index1 < 0 || index2 < 0) return 0;

        // STEP 1,2: Base case + LOGIC --> MATCH

        if (text1[index1] == text2[index2]){
            return 1 + helper(index1- 1, index2 - 1, text1, text2);
        }

        // STEP 2: LOGIC --> NOT MATCH --> split into 2 shifts

        return 0 + max (helper(index1- 1, index2, text1, text2), 
                    helper(index1, index2 - 1, text1, text2) );

        // STEP 3: explicit returning not needed as all the cases are covered already

    }

public:
    int longestCommonSubsequence(string text1, string text2) {
        return helper(text1.size() - 1, text2.size() - 1, text1, text2);
    }
};

```

## Approach 2: Recursion with Memoization

```cpp

class Solution {

private: 

    int helper (int index1, int index2, string text1, string text2, 
        vector<vector<int>>& dp_table){
      
        // STEP 1: Base cases

        if (index1 < 0 || index2 < 0) return 0;

        if (dp_table[index1][index2] != -1) return dp_table[index1][index2];



        // STEP 1,2: Base case + LOGIC --> MATCH

        if (text1[index1] == text2[index2]){
          
            dp_table[index1][index2] = 1 + helper(index1- 1, index2 - 1, text1, text2, dp_table);

            return dp_table[index1][index2];
          
        }

        // STEP 2: LOGIC --> NOT MATCH --> split into 2 shifts

        dp_table[index1][index2]  = 0 + max (helper(index1- 1, index2, text1, text2, dp_table), 
                                            helper(index1, index2 - 1, text1, text2, dp_table) );

        return dp_table[index1][index2];

        // STEP 3: explicit returning not needed as all the cases are covered already


    }

public:
    int longestCommonSubsequence(string text1, string text2) {

      
        int m = text1.size();
        int n = text2.size();

        vector<vector<int>> dp_table (m, vector<int>(n, -1));

        return helper(m - 1, n - 1, text1, text2, dp_table);
    }
};

```

## Approach 3: Tabulation

## NEW LEARNING --> SHIFTING INDEX TO MAKE OUR PREVIOUS BASE CASE LOGICS WORK

```cpp

class Solution {
public:
    int longestCommonSubsequence(string text1, string text2) {
      
        int m = text1.size();
        int n = text2.size();

        vector<vector<int>> dp_table (m + 1, vector<int>(n + 1, 0));

        // base case initilization

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
};

```
