# Longest Common Sub - Sequence

## Approach 1 --> Pure Recursion

#### THE 3 LAYER COMPARISON

- Match
- Not match - shift 1
- Not Match - Shift 2

#### HOW DOES THIS WORK?

- we start from the LAST index of both strings --> go backwards towards 0
- at every (index1, index2) we ask --> what is LCS of text1[0..index1] and text2[0..index2] ?

1. MATCH --> both chars same --> take it (+1) and move BOTH pointers back
2. NOT MATCH --> we cannot take both --> so try BOTH options and take max:
   - shift text1 only --> helper(index1 - 1, index2)
   - shift text2 only --> helper(index1, index2 - 1)
3. BASE --> if either index goes < 0 --> no string left --> LCS = 0

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

#### WHAT DOES THE DP TABLE MEAN?

- dp_table[index1][index2] = LCS length of text1[0..index1] and text2[0..index2]
- ROW = index in text1
- COL = index in text2
- size = m x n --> because indexes go from 0 .. m-1 and 0 .. n-1
- same 3-layer logic as Approach 1 --> just STORE the answer before returning so we dont recompute the same (index1, index2)

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

#### HOW DO WE CONVERT MEMO --> TABULATION?

- in memo, base was index < 0 --> return 0 --> BUT arrays cannot have -1 index
- so we SHIFT everything by +1:
  - old index1 / index2  -->  new index1 / index2 in the table
  - char access becomes text1[index1 - 1] / text2[index2 - 1]
  - old base (index < 0)  -->  now row 0 and col 0 are all 0s (dummy empty string)
- dp_table size becomes (m+1) x (n+1)
- dp_table[i][j] = LCS of first i chars of text1 and first j chars of text2
- fill bottom-up: i = 1..m , j = 1..n --> same MATCH / NOT MATCH logic as before
- answer sits at dp_table[m][n]
- NOTE --> no need for explicit base-case loops --> table is already initialized with 0s --> row 0 and col 0 are already covered

```cpp
class Solution {
public:
    int longestCommonSubsequence(string text1, string text2) {
        int m = text1.size();
        int n = text2.size();

        // already all 0s --> base case (row 0 / col 0 = empty string) is done
        vector<vector<int>> dp_table (m + 1, vector<int>(n + 1, 0));

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
