## Solution 1: Every UNSUCCESSFUL traversal adds an edge in perimeter
#### **MAIN LOGIC** --> there are different types of failed explorations --> we only increment perimeter of the reason was WATER or OUT OF BOUNDS --> since already visited nodes dont result in adding perimeter

```cpp
class Solution {

private:

    int dfs(vector<vector<int>>& grid, vector<vector<int>>& visited, int row, int col){

        // base case is NOT the zero one since we are validating that before calling recursion

        // base case - mark visited 
        visited[row][col] = 1;

        int peri = 0;

        // find neighbors = --> permieter of this node is decided by:
            // 1. neigbors being present/absent
            // 2. what neighbors bring

        int directions [4][2] = {{-1, 0}, {1, 0}, {0, -1}, {0, 1}};

        for (int i = 0; i < 4; i++){
            int nrow = row + directions[i][ 0];
            int ncol = col + directions[i][1];

            // lets see - who makes it far
            // if succesful explore --> increment their count peri in us
            // WHAT IS SUCCESS? --> inbound && land && non-visited 
            if(nrow >= 0 && nrow < grid.size() && ncol >= 0 && ncol < grid[0].size() &&
            grid[nrow][ncol] == 1 &&
            visited[nrow][ncol] == 0){

                peri += dfs(grid, visited, nrow, ncol);
            
            }

            // if failed explored --> increment peri by 1
            // MAIN LOGIC
                // --> there can be many reason of failure 
                // --> we only increment if failure was due to WATER OR out of bounds
            else if(nrow < 0 || nrow >= grid.size() || ncol < 0 ||  ncol >= grid[0].size() || grid[nrow][ncol] == 0){
                peri += 1;
            }
        }

        // here we get the final perimeter returned by this node
        return peri;

    }

public:
    int islandPerimeter(vector<vector<int>>& grid) {

        // 1. find the starting land

        int m = grid.size();
        int n = grid[0].size();

        int row = -1;
        int col = -1;
        bool found = false;

        for(int i = 0; i < m && found == false; i++){
            for(int j = 0; j < n && found == false; j++){
                if(grid[i][j] == 1){
                    row = i;
                    col = j;
                    found = true; // stops both loops
                }
            }
        }

        vector<vector<int>> visited (m, vector<int>(n, 0));

        return dfs(grid, visited, row, col);

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