

## Solution 1: Every UNSUCCCESFUL traversal adds an edge in perimeter


```cpp
class Solution {

private:
    void dfs_rec(vector<vector<int>>& grid, vector<vector<int>>& visited, int row, int col, int& peri){

        int m = grid.size();
        int n = grid[0].size();


        visited[row][col] = 1;


        // check neighbors

        int directions [4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

        for (int i = 0; i < 4; i++){
            int nrow = row + directions[i][0];
            int ncol = col + directions[i][1];

            // valid & land & unvisited --> no peri update and recurse
            if (nrow >= 0 && nrow < m &&
            ncol >= 0 && ncol < n &&
            grid[nrow][ncol] == 1 &&
            visited[nrow][ncol] != 1) dfs_rec(grid, visited, nrow, ncol, peri);

            // invalid or water --> peri update and continue
            else if (nrow < 0 || nrow >= m ||
            ncol < 0 || ncol >= n || grid[nrow][ncol] != 1){
                peri += 1;
                continue;
            }
        }
    }

public:
    int islandPerimeter(vector<vector<int>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        int row = 0;
        int col = 0;
        bool found = false;

        for(int i = 0; i < m && !found; i++){
            for (int j = 0; j < n && !found; j++){
                if (grid[i][j] == 1){
                    row = i;
                    col = j;
                    // Found the starting point
                    found = true;
                }
            }
        }

        int peri = 0;
        vector<vector<int>> visited (m, vector<int>(n, 0));
        dfs_rec(grid, visited, row, col, peri);

        return peri;


    }
};
```

## Solution 2: Can optimize space using same grid overwites

```cpp

class Solution {

private:
    void dfs_rec(vector<vector<int>>& grid, int row, int col, int& peri){

        int m = grid.size();
        int n = grid[0].size();
        grid[row][col] = 2;

        // check neighbors

        int directions [4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

        for (int i = 0; i < 4; i++){
            int nrow = row + directions[i][0];
            int ncol = col + directions[i][1];

            // valid & land & unvisited --> no peri update and recurse
            if (nrow >= 0 && nrow < m &&
            ncol >= 0 && ncol < n &&
            grid[nrow][ncol] == 1) dfs_rec(grid, nrow, ncol, peri);

            // invalid or water --> peri update and continue
            else if (nrow < 0 || nrow >= m ||
            ncol < 0 || ncol >= n ||
            grid[nrow][ncol] == 0 ){
                peri += 1;
                continue;
            }
        }
    }

public:
    int islandPerimeter(vector<vector<int>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        int row = 0;
        int col = 0;
        bool found = false;

        for(int i = 0; i < m && !found; i++){
            for (int j = 0; j < n && !found; j++){
                if (grid[i][j] == 1){
                    row = i;
                    col = j;
                    // Found the starting point
                    found = true;
                }
            }
        }

        int peri = 0;
        dfs_rec(grid, row, col, peri);

        return peri;


    }
};

```