## INTUITION: START FROM THE BORDER
```bash
- traverse each zero - and mark them visited in a visited grid
- after all 4 traversals done:
    mark those zeroes as x which were not visited 
```

# INTUITION SAYS --> "if it was not visited and is not on border -- THEN IT IS BOUND TO BE SURROUNDED BY X's"

*/

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
            if(board[i][0] == 'O'){
                dfs(i, 0, visited, board);
            }
            if(board[i][n-1] == 'O'){
                dfs(i, n-1, visited, board);
            }
        }

        // both rows
        for (int i = 0; i < n; i++){
            if(board[0][i] == 'O'){
                dfs(0, i, visited, board);
            }
            if(board[m-1][i] == 'O'){
                dfs(m-1, i, visited, board);
            }
        }



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