

## Using Optimized Brute --> Basically with early termination, as I am not checking every column completely



```cpp

/*

pick a row
    - take its first element
    - iterate over all 0th items of cols
    - if there is a match:
        - get in a while loop to compare all items
        - if reached end --> then add to result


*/


class Solution {
public:
    int equalPairs(vector<vector<int>>& grid) {

        int n = grid.size();
        int result = 0;

        for(int row = 0; row < n; row++){

            int element = grid[row][0];

            for(int col = 0; col < n; col++){
                if(grid[0][col] == element){

                    // loop of comparisions
                    bool flag = true;

                    for(int i = 0; i < n; i++){

                        if(grid[row][i] != grid[i][col]){ // fucked up midway
                            flag = false;
                            break;
                        }

                    }

                    // if flag = true; // that was a sucess --> update result

                    if(flag == true){
                        result++;
                    }
                    // if flag = false; // that was a fuckup --> continue with new columns
                    else continue;
                }

                // else this col is not a match --> continue to next column
            }

        }

        return result;

        
    }
};

```

## Better --> Using Map 

### INTUITION --> We need to use either map with vector as key ---OR--- unordered_map with using stringified version of key


```cpp


class Solution {
public:
    int equalPairs(vector<vector<int>>& grid) {

        // 1. creating map

        unordered_map <string, int> mp;


        // 2. push all rows in map 

        int n = grid.size();

        for(int row = 0; row < n; row++){
            // 2.1 declare a string
            
            string complete_row = "";

            for(int col = 0; col < n; col++){
                
                // 2.2 stringify and keep on building string
                complete_row += to_string(grid[row][col]);
                complete_row.push_back('#'); // need a delimiter, since 11 22 33 is not same as 1 122 33
            }

            // 2.3 push in map

            mp[complete_row]++; // we are incrementing the count since if there are same rows then for a matching column, I can directly add the frequency of similar rows --> AND BASICALLY THAT IS THE POINT OF USING MAP or else we could have also used a set.

        }


        // now push all columns and while pushing check if there is match checking if there is a match

         // 3. push all cols in map 

        int result = 0;

        for(int col = 0; col < n; col++){
            
            string complete_col = "";

            for(int row = 0; row < n; row++){
                
                complete_col += to_string(grid[row][col]);
                complete_col.push_back('#'); // need a delimiter, since 11 22 33 is not same as 1 122 33
            }

            // 3.3 push in map
            if (mp.find(complete_col) != mp.end()) result += mp[complete_col];

        }

        return result;
    }
};


```