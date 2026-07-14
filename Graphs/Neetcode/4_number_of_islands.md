# INTUITIONS:

```bash
1. every element in the adjacency matrix acts as a node
2. we start from first row, first col
    - If we find a "1"
        - island++
        - then we initialize the BFS --> each time it finds someone with 1 we mark it visted as 2
    - when it ends we  continue with traversal inside matrix
```




## Solution 1 - Using BFS

```cpp
class Solution {

private: 
    void DFS (int i, int j, vector<vector<char>>& grid){

        int m = grid.size();
        int n = grid[0].size();

// ------ ------ ----VERY IMPPPPPPP ------ ------ ------ ----
        // check if the current indexes are valid or not
        if (i < 0 || i >= m || j < 0 || j >= n) return;


        // 1. -------BASE CASES-----> can be 0,1,2
 
        // 1.1 IF LAND or already visited --> RETURN 
        if (grid[i][j] == '0' || grid[i][j] == '2') return;
       

        // 1.2 IF VALID THEN MARK VISITED
        grid[i][j] = '2';

        
// ------ ------ ----VERY IMPPPPPPP ------ ------ ------ ----
       
        // 2. EXPLORE --> the correctness of indexes && validness of content will be checked in their individual recurive calls
        DFS(i, j-1, grid);
        DFS(i, j+1, grid);
        DFS(i-1, j, grid);
        DFS(i+1, j, grid);
        
    }


public:
    int numIslands(vector<vector<char>>& grid) {
        
        int m = grid.size();
        int n = grid[0].size();

        int islands = 0;

        for (int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){

                if(grid[i][j] == '1'){
                    
                    islands++;

                    DFS(i, j, grid);

                }

            }
        }

        return islands;
        
    }
};
```


## Solution 2: Using Recusrive DFS

```cpp

class Solution {

private:

    void dfs_rec (vector<vector<char>>& grid, vector<vector<int>>& visited, int row, int col){
        
        // 1. basics
        visited[row][col] = 1;
        
        int m = grid.size();
        int n = grid[0].size();

        // 2. find neighbor

        int delta[4][2] = {{0, -1}, {0, 1}, {1, 0}, {-1, 0}};

        for(int i = 0; i < 4; i++){

            int nrow = row + delta[i][0];
            int ncol = col + delta[i][1];

            // neighbor index valid && land && unvisited
            if (nrow >= 0 && nrow < m && ncol >=0 && ncol < n &&
            grid[nrow][ncol] == '1' &&
            visited[nrow][ncol] == 0){
                dfs_rec(grid, visited, nrow, ncol);
            }
        }

        return;
    }


public:
    int numIslands(vector<vector<char>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        vector<vector<int>> visited (m , vector<int>(n, 0));

        int counter = 0;

        for (int i = 0; i < m; i++){
            for(int j = 0; j < n; j++){
                if (grid[i][j] == '1' && visited[i][j] == 0){
                    counter++;
                    dfs_rec(grid, visited, i, j);
                }
            }
        }

        return counter;
        
    }
};

```
## Learnings --> Check the grid index validaity INDIVIDUALLY IN EVERY RECURSION before making ANYYYYYY changes
