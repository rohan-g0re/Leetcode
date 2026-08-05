## INTUITION --> Prefix sum-LIKE logic by using map


### Solution 1 --> but got MLE

```cpp


class Solution {
public:
    int countCoveredBuildings(int n, vector<vector<int>>& buildings) {


        unordered_map<int, int> rows;
        unordered_map<int, int> cols;
        unordered_map<int, int> prows;
        unordered_map<int, int> pcols;

        vector<vector<int>> grid (n, vector<int>(n, 0));

        // 1. fill the grid and global frequency maps rows AND cols

        for (int i = 0; i < buildings.size(); i++){

            int row = buildings[i][0] - 1; // making them zero-indexed
            int col = buildings[i][1] - 1; // making them zero-indexed

            rows[row]++;
            cols[col]++;


            grid[row][col] = 1;
        }

        int covered = 0;


        // 2. iterate on the grid

        for(int row = 0; row < n; row++){
            for(int col = 0; col < n; col++){

                // 1.1 if we find a 1

                if(grid[row][col] == 1){

                    // 1.2 check if there has been 1 in same row and same col in "prev" tables

                    if(prows.find(row) != prows.end() && pcols.find(col) != pcols.end()){ // which means there is present
                        
                        // 1.3 check if present in global table

                        if(rows[row] - prows[row] - 1 > 0 && cols[col] - pcols[col] - 1 > 0){ // valid count in right and down
                        // -1 for subtracting the current element

                            covered++;
                        }
                    }


                    // 1.4 update the rfeq tables when you got a 1 in grid

                    prows[row]++;
                    pcols[col]++;
                }
            }
        }

        return covered;

    }
};

```


#### Either we need to remove grid altogether or prefix tables that we maintain --> I think it should be grid


## Solution 2 --> without grid BUT sorted the array so as to maintain the order wrt rows and columns

```cpp


class Solution {
public:
    int countCoveredBuildings(int n, vector<vector<int>>& buildings) {


        unordered_map<int, int> rows;
        unordered_map<int, int> cols;
        unordered_map<int, int> prows;
        unordered_map<int, int> pcols;

        // vector<vector<int>> grid (n, vector<int>(n, 0));

        // 1. fill the grid and global frequency maps rows AND cols

        for (int i = 0; i < buildings.size(); i++){

            int row = buildings[i][0] - 1; // making them zero-indexed
            int col = buildings[i][1] - 1; // making them zero-indexed

            rows[row]++;
            cols[col]++;


            // grid[row][col] = 1;
        }

        int covered = 0;

        // IMPORTANT --> the points in buildings are not in the sorted order, therefore an element which should have been previous (left & up) can be later in the array --> therefore we need to sort

        sort(buildings.begin(), buildings.end());


        // 2. iterate on the buildings array

        for(int i = 0; i < buildings.size(); i++){

            int row = buildings[i][0] - 1; // making them zero-indexed
            int col = buildings[i][1] - 1; // making them zero-indexed

            // 2.1 check if there has been 1 in same row and same col in "prev" tables

            if(prows.find(row) != prows.end() && pcols.find(col) != pcols.end()){ // which means there is present
                
                // 2.2 check if present in global table

                if(rows[row] - prows[row] - 1 > 0 && cols[col] - pcols[col] - 1 > 0){ // valid count in right and down
                // -1 for subtracting the current element

                    covered++;
                }
            }

            // 1.4 update the rfeq tables when you got a 1 in grid

            prows[row]++;
            pcols[col]++;
        }

        return covered;

        
    }
};

```


## Solution 3 --> OPTIMAL --> 4 vectors to maintain max and min for rows and columns

- minrow[abc] = xyz --> in column abc , xyz is the minimum row that is filled
- maxrow[abc] = xyz --> in column abc , xyz is the maximum row that is filled

- mincol[abc] = xyz --> in row abc , xyz is the minimum col that is filled
- maxcol[abc] = xyz --> in row abc , xyz is the maximum col that is filled


```cpp


class Solution {
public:
    int countCoveredBuildings(int n, vector<vector<int>>& buildings) {


        vector<int> minrow(n, n); // using "n" as a default fill for max
        vector<int> maxrow(n); 
        vector<int> mincol(n, n); // using "n" as a default fill for max
        vector<int> maxcol(n); 
    

        // 1. fill the maximum and minimum value  in vectors

        for (auto& p : buildings){

            int row = p[0] - 1; // making them zero-indexed
            int col = p[1] - 1; // making them zero-indexed

            minrow[col] =  min(minrow[col], row);
            maxrow[col] =  max(maxrow[col], row);

            mincol[row] =  min(mincol[row], col);
            maxcol[row] =  max(maxcol[row], col);
        }

        int covered = 0;

        for(auto& p : buildings){
            int row = p[0] - 1;
            int col = p[1] - 1;

            if( row > minrow[col] && row < maxrow[col] && col > mincol[row] && col < maxcol[row]){
                covered++;
            }
        }
        return covered;
    }
};


```