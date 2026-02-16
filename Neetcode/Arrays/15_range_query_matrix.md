
## BRUTE: a nested loop on the resctange everytime


```cpp
class NumMatrix {
private:
    vector<vector<int>> matrix;

public:
    NumMatrix(vector<vector<int>>& matrix) {
        this -> matrix = matrix;        
    }
    
    int sumRegion(int row1, int col1, int row2, int col2) {
        
        int sum = 0;
        for (int i = row1; i <= row2; i++ ){
            for (int j = col1; j <= col2; j++){
                sum += matrix[i][j];
            }
        }

        return sum;
    }
};

```

## Optimal --> Using 2D Prefix Sum and storing the values in a prefix table - so that we can retrieve the sum from it

#### We are basically saying that every entry in the prefix table is the sum of the rectangle where you  total sum is stored in the bottom right corner of the rectangle. 


### INTUITION:
- Precompute a prefix sum matrix where ps_matrix[i][j] stores the sum 
  of all elements in the rectangle from (0,0) to (i-1,j-1) in the original matrix.
- We add an extra row and column of zeros as padding to avoid boundary checks.

### BUILDING PREFIX SUM:

##### For each cell ps_matrix[i][j]:
  1. Add the current element: matrix[i-1][j-1]
  2. Add sum from above: ps_matrix[i-1][j]
  3. Add sum from left: ps_matrix[i][j-1]
  4. Subtract overlap (counted twice): ps_matrix[i-1][j-1]

### QUERYING A REGION (row1,col1) to (row2,col2):
##### Use inclusion-exclusion principle -->
    
```cpp
Sum = Total rectangle from origin to (row2,col2)
        - Rectangle above the region
        - Rectangle left of the region
        + Overlapping corner (was subtracted twice)
```


##### Complexities

- TIME COMPLEXITY: O(m×n) preprocessing, O(1) per query
- SPACE COMPLEXITY: O(m×n)


### Code

```cpp


class NumMatrix {
private:

    // MEMBER VARIABLE because after the constructor ends, everything given to the constructor and declared in the constructor disappears.
    vector<vector<int>> ps_matrix;


public:
    NumMatrix(vector<vector<int>>& matrix) {

        int rows = matrix.size();
        int cols = matrix[0].size();

        ps_matrix = vector<vector <int>> (rows + 1, vector<int>(cols + 1, 0));


        // starting from 1

        for (int i = 1; i <= rows; i++){
            for (int j = 1; j <= cols; j++){
                
                ps_matrix[i][j] =   matrix[i-1][j-1]            //current element
                                    + ps_matrix[i-1][j]      // sum from above
                                    + ps_matrix[i][j-1]     // sum from left
                                    - ps_matrix[i-1][j-1];  // since common was added twice
            }
        }
    }
    
    int sumRegion(int row1, int col1, int row2, int col2) {
        
        // add 1 since we are comparing in prefix sum matrix
        row1++, col1++, row2++, col2++;

        int final_sum = ps_matrix[row2][col2] //actual 
                        - ps_matrix[row1-1][col2] //above
                        - ps_matrix[row2][col1-1] // left
                        + ps_matrix[row1-1][col1-1]; // since common was subtracted twice

        return final_sum;
    }
};


```