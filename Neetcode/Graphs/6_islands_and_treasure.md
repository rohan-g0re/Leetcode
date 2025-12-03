
## INTUITION:
- we need to do bfs/dfs on this to find the distance
- snapshot time to keep a track of actual distance covered


## BRUTE FORCE: 
1. initialize dfs from every land cell

## BETTER:
1. Use recursive such that we get min distance from treasure
2. Mark visited by 2



## FAILED ATTEMPT - Recusrive dfs bottom up --> not the best way to do stuff because inherently it should be top down

#### MY FAILED CODE:
```cpp
class Solution {

private: 

int dfs_recursive(int row, int col, vector<vector<int>>& grid){

    // check index validity

    
    int m = grid.size();
    int n = grid[0].size();
    
    if (row < 0 || row >= m || col < 0 || col >= n ) return INT_MAX;

    // now that its valid


    // base case --> if == 0 --> return 1;
    if (grid[row][col] == 0) return 1;

    // base case --> water(-1) or already visited(-2)
    if (grid[row][col] < 0) return INT_MAX;


    int distance = INT_MAX;
    // int right

    // mark visited if land
    if (grid[row][col] == INT_MAX){

        // mark visited
        grid[row][col] = -2 ;

        
        // check for neighbors

        int deltarow[] = {-1, 0, 1, 0};
        int deltacol[] = {0, 1, 0, -1};

        for (int i = 0; i < 4; i++){
            int n_row = row + deltarow[i];
            int n_col = col + deltacol[i];

            distance = min (distance, dfs_recursive(n_row, n_col, grid));
        }

    }

    grid[row][col] = distance;

    return 1 + grid[row][col];


}

public:
    void islandsAndTreasure(vector<vector<int>>& grid) {

        // driver upon the grid

        int m = grid.size();
        int n = grid[0].size();
        
        for (int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){
                if (grid[i][j] == INT_MAX){
                    int x = dfs_recursive(i, j, grid);
                }
            }
        }

    }
};
```


#### CORRECT CODE:

```cpp

class Solution {

private:
    const int INF = 2147483647;        // given INF in the problem
    const int BIG = 1000000000;        // our internal "infinite" distance

    int dfs_recursive(int row, int col, vector<vector<int>>& grid) {
        int m = grid.size();
        int n = grid[0].size();

        // 1. Out-of-bounds → no path
        if (row < 0 || row >= m || col < 0 || col >= n) {
            return BIG;
        }

        // 2. Water → no path
        if (grid[row][col] == -1) {
            return BIG;
        }

        // 3. Treasure → distance 0
        if (grid[row][col] == 0) {
            return 0;
        }

        // 4. Already computed distance (positive and not INF) → reuse it
        //    Any positive value < INF now represents a final distance.
        if (grid[row][col] > 0 && grid[row][col] < INF) {
            return grid[row][col];
        }

        // 5. Detect cycles: if we hit a cell currently in the recursion stack
        //    (marked as -2), treat it as no path.
        if (grid[row][col] == -2) {
            return BIG;
        }

        // 6. This is an unprocessed land cell: grid[row][col] == INF.
        //    Mark as "visiting" to avoid cycles.
        grid[row][col] = -2;

        int deltarow[4] = {-1, 0, 1, 0};
        int deltacol[4] = {0, 1, 0, -1};

        int best = BIG;

        // 7. Explore neighbors to find the best distance to a treasure
        for (int k = 0; k < 4; k++) {
            int nr = row + deltarow[k];
            int nc = col + deltacol[k];

            int candidate = dfs_recursive(nr, nc, grid);
            if (candidate < best) {
                best = candidate;
            }
        }

        // 8. If no neighbor can reach a treasure, keep this cell as INF.
        //    Otherwise, distance = best + 1.
        if (best == BIG) {
            grid[row][col] = INF;          // unreachable → keep INF
            return INF;                    // return INF too
        } else {
            grid[row][col] = best + 1;     // store final distance
            return grid[row][col];         // and return it
        }
    }

public:
    void islandsAndTreasure(vector<vector<int>>& grid) {
        int m = grid.size();
        int n = grid[0].size();

        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                // Only compute for land cells that are still INF
                if (grid[i][j] == INF) {
                    dfs_recursive(i, j, grid);
                }
            }
        }
    }
};

```


## SOLUTION 2 --> CORRECT WAY OF DFS --> TOP-DOWN --> start from treasure


### CODE:

```cpp
class Solution {
public:
    void islandsAndTreasure(vector<vector<int>>& grid) {
        int m = grid.size();
        int n = grid[0].size();

        // Start DFS from all treasure cells (value 0)
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 0) {
                    dfs(grid, i, j, 0);
                }
            }
        }
    }

private:
    void dfs(vector<vector<int>>& grid, int r, int c, int dist) {
        int m = grid.size();
        int n = grid[0].size();

        // bounds
        if (r < 0 || c < 0 || r >= m || c >= n) return;

        // water
        if (grid[r][c] == -1) return;

        // pruning:
        // if we already have a better distance stored, stop
        if (dist > grid[r][c]) return;

        // update distance
        grid[r][c] = dist;

        // explore neighbors
        dfs(grid, r + 1, c, dist + 1);
        dfs(grid, r - 1, c, dist + 1);
        dfs(grid, r, c + 1, dist + 1);
        dfs(grid, r, c - 1, dist + 1);
    }
};

```


# CRAZY --> POPULAR SOLUTION 3 --> BFS

```cpp
class Solution {
public:
    void islandsAndTreasure(vector<vector<int>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        queue<pair<int, int>> q;

        // ----------------------------------------------------
        // 1. Push ALL treasure cells (value = 0) into the BFS queue
        //    These are our MULTIPLE starting points (multi-source BFS)
        // ----------------------------------------------------
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 0) {
                    q.push({i, j});
                }
            }
        }

        // Directions for top, right, bottom, left
        vector<pair<int,int>> dirs = {{-1,0},{0,1},{1,0},{0,-1}};

        // ----------------------------------------------------
        // 2. BFS from all treasure cells simultaneously
        // ----------------------------------------------------
        while (!q.empty()) {

            auto [r, c] = q.front();
            q.pop();

            // Explore all 4 neighbors
            for (auto& d : dirs) {

                int nr = r + d.first;   // new row
                int nc = c + d.second;  // new col

                // Skip out-of-bounds positions
                if (nr < 0 || nc < 0 || nr >= m || nc >= n)
                    continue;

                // Skip water (-1) or treasure (0)
                if (grid[nr][nc] == -1)
                    continue;

                // ---------------------------------------------
                // KEY CHECK:
                // Only update the neighbor IF the new distance
                // is strictly better (smaller) than what's there.
                //
                //    If current cell has distance grid[r][c],
                //    then neighbor becomes  grid[r][c] + 1.
                //
                // Initially, neighbors are INF (2147483647),
                // so they always get updated the first time.
                // ---------------------------------------------
                if (grid[nr][nc] > grid[r][c] + 1) {
                    grid[nr][nc] = grid[r][c] + 1;
                    q.push({nr, nc});  // Push updated cell into BFS queue
                }
            }
        }
    }
};

```







