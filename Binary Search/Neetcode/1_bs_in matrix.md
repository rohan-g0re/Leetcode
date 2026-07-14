# ALGO: 

### 1. binary search on the first values of each row to find the correct row which might have the target  

### 2. binary search on that row


```cpp


class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        
        int top_row = 0;
        int bottom_row = matrix.size() - 1;
        
        int m = matrix.size() - 1;
        int n = matrix[0].size() - 1;
        
        
        int final_row = -1;

        while (top_row <= bottom_row){
            
            int mid = (top_row + bottom_row ) /2;

            if (target >= matrix[mid][0] && target <= matrix[mid][n]){
                final_row = mid;
                break;
            }
            
            else if (target < matrix[mid][0]){

                bottom_row = mid - 1;

            }
            else{
                top_row = mid + 1;
            }
        }

        // VERY IMPORTANT --> this means that our first loop did not find a valid row and ended 
        if (final_row == -1) return false;


        // we got the row 

        int low = 0;
        int high = n;
        
        while(low <= high){
            
            int mid = (low + high ) /2;

            if (target == matrix[final_row][mid]){
                return true;
            }
            
            else if (target < matrix[final_row][mid]){

                high = mid - 1;

            }
            else{
                low = mid + 1;
            }
        }

        return false;

    }
};

```