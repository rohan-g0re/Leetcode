
## INTUITION:
- we need to do bfs/dfs on this to find the distance
- snapshot time to keep a track of actual distance covered


## BRUTE FORCE: 
1. initialize dfs from every land cell
##### OR
1. Use recursive such that we get min distance from treasure
2. Mark visited by 2


# MAIN INTUITION --> Rotten Oranges Intuition --> dont always try to start from grid--> if you have a target in head (treasure/orange/cross) --> **YOU CAN STAT FROM THERE AND THEN EXPLORE THE GRID**



## SOLUTION 1 --> DFS --> TOP-DOWN --> start from treasure


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
    void dfs(vector<vector<int>>& grid, int row, int col, int dist) {

        int m = grid.size();
        int n = grid[0].size();

        /*
        this cell can be:
        - land
        - treasure (invoked by driver)
        --> eitherways we need a minimum value --> being treasure already gives zero --> so no need to handle it separately
        */

        // mark the distance
        grid[row][col] = dist;


        /*
        neighbor can be:
        invalid index
        water
        land
        treasure

        also - neighbor should become BETTER by exploring --> OR ELSE WE WONT EXPLORE IT
        */

        int delta[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

        for(int i = 0; i < 4; i++){
            int nrow = row + delta[i][0];
            int ncol = col + delta[i][1];

            if(nrow >= 0 && nrow < m && ncol >= 0 && ncol <n && // valid index
            grid[nrow][ncol] > 0 &&         // not land or treasure
            grid[nrow][ncol] > dist + 1     // exploring will make neighbor's value better
            ){
                dfs(grid, nrow, ncol, dist + 1); // all sanity checks are done before --> hence call recursion and mark distance directly
            }
        }

        return;
    }
};


```


# SOLUTION 2 --> Popular solution, Same logic --> **BFS**

```cpp
class Solution {
public:
    void islandsAndTreasure(vector<vector<int>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        queue<pair<int, int>> q;

        // push ALL treasures --> multi-source BFS
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (grid[i][j] == 0) {
                    q.push({i, j});
                }
            }
        }

        int delta[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

        while (!q.empty()) {

            int r = q.front().first;
            int c = q.front().second;
            q.pop();

            for (int i = 0; i < 4; i++) {

                int nr = r + delta[i][0];
                int nc = c + delta[i][1];

                /*
                neighbor can be:
                invalid index
                water
                land
                treasure

                also - neighbor should become BETTER by exploring --> OR ELSE WE WONT EXPLORE IT
                */

                if (nr >= 0 && nr < m && nc >= 0 && nc < n &&   // valid index
                    grid[nr][nc] > 0 &&                         // not water / treasure
                    grid[nr][nc] > grid[r][c] + 1               // exploring makes neighbor better
                ){
                    // mark distance + push
                    grid[nr][nc] = grid[r][c] + 1;
                    q.push({nr, nc});
                }
            }
        }
    }
};

```
