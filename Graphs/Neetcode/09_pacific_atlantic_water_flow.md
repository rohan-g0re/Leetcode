### INTUITION --> Start traversal from rows and cols touching either ocean --> keep 2 different visited grids for both of them --> recursive dfs --> at the end: compare both the grids --> points which were REACHED by both oceans are the answer 

#### IMP LOGIC --> as we are going from ocean to nodes --> "The NEXT ACCEPTABLE NODE is EQUAL OR GREATER in HEIGHT"  (reverse logic, bcoz rain wll be on nodes)


```cpp
class Solution {
private:
    void dfs(int row, int col, vector<vector<int>>& heights, 
             vector<vector<bool>>& visited) {
        int m = heights.size();
        int n = heights[0].size();
        
        visited[row][col] = true;
        
        int delta[4][2] = {{-1,0}, {1,0}, {0,-1}, {0,1}};
        
        for (int i = 0; i < 4; i++) {
            int nrow = row + delta[i][0];
            int ncol = col + delta[i][1];
            
            // SANITY CHECK FOR NEIGHBOR
            if (nrow >= 0 && nrow < m && ncol >= 0 && ncol < n && // valid index
            visited[nrow][ncol] == false && // should not be visited before
            heights[nrow][ncol] >= heights[row][col]){  // should be taller (reverse logic)
                dfs(nrow, ncol, heights, visited);
            }
        }
        return;
    }

public:
    vector<vector<int>> pacificAtlantic(vector<vector<int>>& heights) {
        int m = heights.size();
        int n = heights[0].size();
        
        vector<vector<bool>> pacific(m, vector<bool>(n, false));
        vector<vector<bool>> atlantic(m, vector<bool>(n, false));
        
        // Start DFS from Pacific ocean borders (top row + left column)
        for (int i = 0; i < m; i++) {
            dfs(i, 0, heights, pacific);  // Left column
        }
        for (int j = 0; j < n; j++) {
            dfs(0, j, heights, pacific);  // Top row
        }
        
        // Start DFS from Atlantic ocean borders (bottom row + right column)
        for (int i = 0; i < m; i++) {
            dfs(i, n-1, heights, atlantic);  // Right column
        }
        for (int j = 0; j < n ; j++) {
            dfs(m-1, j, heights, atlantic);  // Bottom row
        }
        
        // Find cells reachable by both oceans
        vector<vector<int>> result;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (pacific[i][j] && atlantic[i][j]) {
                    result.push_back({i, j});
                }
            }
        }
        return result;
    }
};
```
