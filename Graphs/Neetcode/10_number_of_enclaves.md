# INTUITION:
#### 1. BFS/DFS from 1's that are on the boundary --> only traverse 1s --> mark visited in a visited grid
#### 2. next for loop --> we look for 1's which are NOT VISITED --> thats the answer



## CODE:

```cpp


class Solution {

// Let's do it recursively. 
void dfs (vector<vector<int>>& grid, vector<vector<int>>& visited, int row, int col){

    
    int m = grid.size();
    int n = grid[0].size();

    // 1. base cases: if already visited - return OR mark visited
    // note: we can also add the case to invalid index here BUT instead we will be adding it in traversal logic

    if (visited[row][col] == 1) return;
    
    visited[row][col] = 1;


    // 2. Recursion Logic

    // 2.1 check neighbors

    int delta[4][2] = {{0, 1}, {0, -1}, {1, 0}, {-1, 0}};

    for(int i = 0; i < 4; i++){
        int nrow = row + delta[i][0];
        int ncol = col + delta[i][1];

        // 2.2 as we said we will check the valid indexes in the recursion logic. 
        
        // valid index && 1 && not visited
        if (nrow >= 0 && nrow < m && ncol >= 0 && ncol < n &&
            grid[nrow][ncol] == 1 &&
            visited[nrow][ncol] != 1){

                dfs(grid, visited, nrow, ncol);
        }
    }
}

public:
    int numEnclaves(vector<vector<int>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        vector<vector<int>> visited(m, vector<int>(n, 0));

        // PART 1: mark 1's that are not part of the answer

        // First and last columns. 
        for (int i = 0; i < m; i++){
            if(grid[i][0] == 1) dfs(grid, visited, i, 0);
            if(grid[i][n-1] == 1) dfs(grid, visited, i, n-1);
        }

        // First and last rows. 
        for (int i = 0; i < n; i++){
            if(grid[0][i] == 1) dfs(grid, visited, 0, i);
            if(grid[m-1][i] == 1) dfs(grid, visited, m-1, i);
        }


        // PART 2: count unvisited 1;
        int counter = 0;

        for (int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){
                if (grid[i][j] == 1 && visited[i][j] != 1) counter++;
            }
        }
        return counter;
    }
};

```