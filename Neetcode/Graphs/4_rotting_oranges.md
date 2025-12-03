## INTERESTING TECHNIQUE USED FOR MEASURING TIME:

##### Before the queue iteration we take the SNAPSHOT of the queue for size, adn only go on fo those many iterations
###### With this we can still keep on pushing elements in queue but the bfs will only be performed on the firsh `snapshot_time` elements
##### When we are done with the `snapshot_time` number of elements --> it basically counts as ONE UNIT TIME, because all that we have/had in the queue for a given snapshot is BASICALLY THE IMMEDIATE NEIGHBORS OF THE ROTTEN ORANGES  

*****


## CODE: 

```cpp
class Solution {
public:
    int orangesRotting(vector<vector<int>>& grid) {

        int m = grid.size();
        int n = grid[0].size();

        int fresh = 0;

        queue <pair<int, int>> q;

        // phase 1 
        for(int i = 0; i < m; i++){
            for (int j = 0; j < n; j++){
                if(grid[i][j] == 1) fresh++;
                else if (grid[i][j] == 2){
                    // push into queue
                    q.push({i, j});
                }
            }
        }

        int time = 0;
        
        while (!q.empty() && fresh > 0){

            int snapshot_time = q.size();

            for(int i = 0; i < snapshot_time; i++){

                // pop stuff 

                int row = q.front().first;
                int col = q.front().second;
                q.pop();

                // check thoer neigh

                int deltarow [] = {-1, 0, +1, 0};
                int deltacol [] = {0, 1, 0, -1};

                for (int i = 0; i < 4; i++){
                    
                    int neighbor_row = row + deltarow[i];
                    int neighbor_col = col + deltacol[i];

                    // validity check 

                    if(neighbor_row >= 0 && neighbor_row < m 
                    && neighbor_col >= 0 && neighbor_col < n
                    && grid[neighbor_row][neighbor_col] == 1){

                        // update grid

                        grid[neighbor_row][neighbor_col] = 2;

                        fresh--;
    
                        // push them back

                        q.push({neighbor_row, neighbor_col});
                    }

                }
            }

            // ONE snapshot of queue has been dealt with and hence all the work till now is done in one unit time

            time++;
        }

        if (fresh == 0) return time;

        return -1;

        
    }
};
```