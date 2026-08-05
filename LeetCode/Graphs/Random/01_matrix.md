# INTUITION:


## 1. NAIVE APPROACH:

We will be using BFS like:
    1. not in a dumb way from every cell --> BUT **ONLY FROM ZEROES  AS THEY ARE THE GOAL STATE --> REVERSE ENGINEERING**
    2. We will use snapshotting to keep a track of steps taken to expand

ALSO:
- we will not be editting the given data and hence we need 2 extra matrices for visited and result


#### CODE

```cpp
class Solution {
public:
    vector<vector<int>> updateMatrix(vector<vector<int>>& mat) {

        int m = mat.size();
        int n = mat[0].size();
        vector<vector<int>> visited (m, vector<int> (n, 0));
        vector<vector<int>> result (m, vector<int> (n, 0));

        // <<row, col,> steps>
        queue <pair <pair<int, int>, int>> q;

        // initial queue filling with zeroes:

        for (int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){
                if(mat[i][j] == 0){
                    // 1. mark in result as zero --> already ZERO

                    // 2. Push in queue
                    q.push({{i, j}, 0});

                    // 3. Mark visited
                    visited[i][j] = 1;
                }
            }
        }

        // Queue is now filled with inital zeroes

        while(!q.empty()){

            int snapshot_size = q.size();


            for (int i = 0; i < snapshot_size; i++){

                int row = q.front().first.first;
                int col = q.front().first.second;
                int dist = q.front().second;
                q.pop();

                // check neighbors

                int delta[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

                for (int i = 0; i < 4; i++){
                    int nrow = row + delta[i][0];
                    int ncol = col + delta[i][1];

                    // neighbor should have valid index && should be unvisited && be 1 --> then mark  distance;

                    if (nrow >= 0 && nrow < m && ncol >= 0 && ncol < n &&
                    visited[nrow][ncol] != 1 &&
                    mat[nrow][ncol] == 1){
                        // 1. mark distance
                        result[nrow][ncol] = dist + 1;

                        // 2. mark visited
                        visited[nrow][ncol] = 1;

                        // 3. push in queue
                        q.push({{nrow, ncol}, dist + 1});
                    }
                }
            }
        }
        return result;
    }
};
```



## 2. CLEANER APPROACH --> No Snapshot BFS - No Visited array - No Double Queues --> Just pure BFS with "distance optimization" as constraint for termination

### INTUITION --> we are **ALREADY STORING** the current best distance in the Result Grid --> **UTILIZE THAT**

### MAIN LOGIC --> How do we not get into an infinite loop? --> The optimizing condition for exploring prevents us from exploring useless loops, and so when the grid gets completely optimized, the algorithm stops.


```cpp

class Solution {
public:
    vector<vector<int>> updateMatrix(vector<vector<int>>& mat) {

        int m = mat.size();
        int n = mat[0].size();

        // create grid --> visited, result
        vector<vector<int>> result (m, vector<int>(n, INT_MAX));
        
        queue <pair<int, int>> q;
                // row, col

        // Phase 1
        for(int i = 0; i < m; i++){
            for(int j = 0; j < n; j++){
                if(mat[i][j] == 0){
                    // 1. push in queue
                    q.push({i, j});

                    // 2. mirror it in result
                    result[i][j] = 0;
                }
            }
        }

        // PHASE 2: processing using BFS

        while(!q.empty()){

            // 1. node
            auto [row, col] = q.front();
            q.pop();

            // neighbors:
            // sanity check --. valid index, if result can be optimized - then choose

            int delta[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

            for(int i = 0; i < 4; i++){
                int nrow = row + delta[i][0];
                int ncol = col + delta[i][1];

                if(nrow >= 0 && nrow < m && ncol >= 0 && ncol < n &&
                result[nrow][ncol] > result[row][col] + 1){ // this optimizing condition is going to prevent us from getting into cyclic loop problem --> since every node is not going to be optimized all the time
                    result[nrow][ncol] = result[row][col] + 1;
                    q.push({nrow, ncol});
                }
            }
        }
        return result;      
    }
};
```


- Could do this on the same grid to make it faster --> Updating the given data is considered a bad practice, and hence for this problem I choose not to update it.