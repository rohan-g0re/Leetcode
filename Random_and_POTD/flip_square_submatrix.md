
### Just using a 2 pointer like approach to swap the values from top and bottom row and then **close-in** the gap between them


```cpp
class Solution {
public:
    vector<vector<int>> reverseSubmatrix(vector<vector<int>>& grid, int x, int y, int k) {

        int rows = grid.size();
        int cols = grid[0].size();

        int top_row = x;
        int bottom_row = x + k - 1;
        
        while(top_row <= bottom_row){

            for(int col = y; col < y + k; col++){
                swap(grid[top_row][col], grid[bottom_row][col]);
            }
            top_row++;
            bottom_row--;
        }

        return grid;

        
    }
};
```