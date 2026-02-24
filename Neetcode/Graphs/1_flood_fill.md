#### Same as "number of islands" but only need to do it for the first (starting) component 

```cpp

class Solution {

private: 
    void DFS (int i, int j, vector<vector<int>>& image, int color, int prev_color){

        int m = image.size();
        int n = image[0].size();

// ------ ------ ----VERY IMPPPPPPP ------ ------ ------ ----
        // check if the current indexes passed are valid or not
        if (i < 0 || i >= m || j < 0 || j >= n) return;


        // 1. -------BASE CASES-----> prev_color, othercolour, target_color already

        // 1.1 IF some other color OR target colour already, then --> RETURN 
        if (image[i][j] != prev_color) return;
       

        // 1.2 IF prev_color THEN MARK VISITED
        image[i][j] = color;

        
// ------ ------ ----VERY IMPPPPPPP ------ ------ ------ ----
       
        // 2. EXPLORE --> the correctness of indexes && validness of content will be checked in their individual recurive calls
        DFS(i, j-1, image, color, prev_color);
        DFS(i, j+1, image, color, prev_color);
        DFS(i-1, j, image, color, prev_color);
        DFS(i+1, j, image, color, prev_color);
        
    }


public:
    vector<vector<int>> floodFill(vector<vector<int>>& image, int sr, int sc, int color) {
          
        int m = image.size();
        int n = image[0].size();

        int prev_color = image[sr][sc];

        // INTERESTING CASE RIGHT HERE ----> if the target pixel already has the target color --> then NO ACTION REQUIRED
        
        if (prev_color == color) return image;

        DFS(sr, sc, image, color, prev_color);

        return image;
        
    }
};

```