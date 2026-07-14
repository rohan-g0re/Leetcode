## INTUITION: START FROM THE BORDER

```bash
- traverse each zero - and mark them visited in a visited grid
- after all 4 traversals done:
    mark those zeroes as x which were not visited 
```

# INTUITION SAYS --> "if it was not visited and is not on border -- THEN IT IS BOUND TO BE SURROUNDED BY X's"


```cpp
class Solution {

private:
    void dfs(int row, int col, vector<vector<int>>& visited, vector<vector<char>>& board){

        int m = board.size();
        int n = board[0].size();

        // if index not valid 

        if (row < 0 || row >= m || col < 0 || col >= n) return;

        if (board[row][col] == 'X') return;

        // here we go index valid
    
        if (board[row][col] == 'O' && visited[row][col] != 1){

            visited[row][col] = 1;

            dfs(row-1, col, visited, board);
            dfs(row+1, col, visited, board);
            dfs(row, col-1, visited, board);
            dfs(row, col+1, visited, board);

        }
        return;
    }

public:
    void solve(vector<vector<char>>& board) {

        int m = board.size();
        int n = board[0].size();

        vector <vector<int>> visited (m, vector<int>(n, 0));
    
        // Both Columns

        for (int i = 0; i < m; i++){
            // leftmost column
            if(board[i][0] == 'O'){
                dfs(i, 0, visited, board);
            }
            // rightmost column
            if(board[i][n-1] == 'O'){
                dfs(i, n-1, visited, board);
            }
        }

        // both rows
        for (int i = 0; i < n; i++){
            // top-most row
            if(board[0][i] == 'O'){
                dfs(0, i, visited, board);
            }
            // bottom-most row
            if(board[m-1][i] == 'O'){
                dfs(m-1, i, visited, board);
            }
        }


        // REMAINING WILL BE TAKEN --> HENCE REPLACE

        for (int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){
                if (board[i][j] == 'O' && visited[i][j] != 1){
                    board[i][j] = 'X';
                }
            }
        } 
    }
};

```

#### A cleaner dfs dunction

```cpp
class Solution {

private:
    void dfs(int row, int col, vector<vector<int>>& visited, vector<vector<char>>& board){

        int m = board.size();
        int n = board[0].size();

        visited[row][col] = 1;

        int delta[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

        for (int i = 0; i < 4; i++){
            int nrow = row + delta[i][0];
            int ncol = col + delta[i][1];

            // neighbor should have valid index && should be unvisited && be a O --> then traverse and  mark  distance;

            if (nrow >= 0 && nrow < m && ncol >= 0 && ncol < n &&
            visited[nrow][ncol] != 1 &&
            board[nrow][ncol] == 'O'){

                // 1. keep O unchanged

                // 2. mark this neighbor visited in its personal recursive call 

                // 3. recurse on neighbor
                dfs(nrow, ncol, visited, board);
            }
        }
        return;
    }


```
