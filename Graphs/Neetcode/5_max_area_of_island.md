## INTUITION: Bfs over components and get area --> Keep a record of the max areas as well



```cpp

class Solution {
private:
    int bfs (int i, int j, vector<vector<int>>& grid){

        queue <pair<int, int>> q;

        q.push({i, j});
        grid[i][j] = 2;

        int area = 1;
        int m = grid.size();
        int n = grid[0].size();


        // find neighbors

        int deltarow[] = {-1, 0, +1, 0};
        int deltacol[] = {0, 1, 0, -1};


        while (!q.empty()){
                
            int actual_row = q.front().first;
            int actual_col = q.front().second;
            q.pop();


            
            for (int i = 0; i < 4; i++){
                int neighbor_row = actual_row + deltarow[i];
                int neighbor_col = actual_col + deltacol[i];

                // check if indexes are valid

                if(neighbor_row >= 0 && neighbor_row < m && neighbor_col >= 0 && neighbor_col < n){
                    
                    // if 1 then update stuff

                    if(grid[neighbor_row][neighbor_col] == 1){
                        
                        q.push({neighbor_row, neighbor_col});

                        area++;
                        grid[neighbor_row][neighbor_col] = 2;
                    }
                    
                }
            }


        }

        return area;
    }

public:
    int maxAreaOfIsland(vector<vector<int>>& grid) {

        int global_max = 0;
        
        int m = grid.size();
        int n = grid[0].size();


        
        // driver

            // if not 0 and 2 pass - else (1) bfs

            // push in queue


        for (int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){

                if (grid[i][j] == 1){
                    int area = bfs(i, j, grid);
                    global_max = max(global_max, area);
                }

            }
        }

        return global_max;
    }
};

```



#### TC --> O(m*n) due to grid + O(V+2E) for BFS 
#### SC --> O(m*n) as we are using the grid