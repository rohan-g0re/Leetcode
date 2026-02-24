# INTUITION:


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