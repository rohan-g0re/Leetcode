## INTUITION:

1. We get a grid region --> **verify** if all cells are the same
2. `verify` returns `{val, isLeaf}`:
   - if BOTH ones and zeroes exist --> NOT a leaf --> return `{anything, false}`
   - if only ones / only zeroes --> IS a leaf --> return `{true/false, true}`
3. **ALWAYS create a node** with that `{val, isLeaf}`
4. Explore depends on leaf:
   - `isLeaf == true` --> done, just return the node
   - `isLeaf == false` --> split into 4 quadrants --> `divide` further on each
5. What we return is ALWAYS the node we just created --> children get attached only when we explore

#### MAIN FLOW (`divide`):

```
gets a grid region
    --> calls verify
    --> create new node with isLeaf values
    --> if not leaf: RECURSIVELY divide into 4 (topLeft, topRight, bottomLeft, bottomRight)
    --> return the node
```

```cpp

/*
// Definition for a QuadTree node.
class Node {
public:
    bool val;
    bool isLeaf;
    Node* topLeft;
    Node* topRight;
    Node* bottomLeft;
    Node* bottomRight;
      
    Node(bool _val, bool _isLeaf) {
        val = _val;
        isLeaf = _isLeaf;
        topLeft = NULL;
        topRight = NULL;
        bottomLeft = NULL;
        bottomRight = NULL;
    }
};
*/

class Solution {

private:

    // returns pair representing { 'val', 'isLeaf'}
    pair<bool, bool> verify(vector<vector<int>>& grid, int row1, int row2, int col1, int col2){

        int ones = 0; 
        int zeroes = 0;

        for(int i = row1; i <= row2; i++){
            for(int j = col1; j <= col2; j++){
                // break if both non-zero
                if(ones != 0 && zeroes != 0) return{false, false}; // we can return anything is leaf is false
              
                // only one of them is zero --> increment
                if(grid[i][j] == 1) ones++;
                else zeroes++;
            }
        }

        if(ones != 0 && zeroes != 0) return{false, false};

        // return the final pair {val, isleaf}
        if(ones > 0){
            return {true, true};
        }
        return {false, true};

    }

    Node* divide(vector<vector<int>>& grid, int row1, int row2, int col1, int col2){

        // - gets a grid
        // - calls verify

        auto pair = verify(grid, row1, row2, col1, col2);
        bool val = pair.first;
        bool leaf = pair.second;

        // - create new node with isleaf values

        Node* node = new Node(val, leaf);

        /*
        what we return is based on the explore step:
            - we are OBVIOUSLY going to return the node that we just created
            - but does it have leaf nodes --> that is to be decided
        */


        // - explore:
        //     if isleaf == false:
        //         divide(furter)
        //         divide(furter)
        //         divide(furter)
        //         divide(furter)

        //     is isleaf== true:
        //         return 

        // ----- EXPLORE if needed ------ 

        if(leaf == false){
          
            int midrow = row1 + (row2 - row1) / 2;
            int midcol = col1 + (col2 - col1) / 2;

            node -> topLeft = divide(grid, row1, midrow, col1, midcol);
            node -> topRight = divide(grid, row1, midrow, midcol + 1, col2);
            node -> bottomLeft = divide(grid, midrow + 1, row2, col1, midcol);
            node -> bottomRight = divide(grid, midrow + 1, row2, midcol + 1, col2);
        }

        // if leaf true or eitherwise  --> we return the node that was created here

        return node;
    }


public:
    Node* construct(vector<vector<int>>& grid) {

        int n = grid.size() - 1;
        return divide(grid, 0, n, 0, n);
      
    }
};
```
