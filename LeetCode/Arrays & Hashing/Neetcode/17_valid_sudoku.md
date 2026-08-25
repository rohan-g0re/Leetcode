#### BRUTE --> separately write loop to check every row, every column and every square

## BETTER --> Doing all of those in ONE PASS ONLY

### INTUITION 1: Use THREE SETS so as to keep track of every cell and RECORD them into all three

### INTUITION 2: IMPORTANT --> A VALID sudoku is NOT a SOLVED Sudoku, but it is an UNSOLVED Sudoku that DOES NOT HAVE INVALID RECORDS --> WHICH MEANS BASICALLY WE NEED TO SOLVE SUCH THAT: WE DONT HAVE DUPLICATES bcox that is invalid

```cpp

class Solution {
public:
    bool isValidSudoku(vector<vector<char>>& board) {

        // 1. 3 maps having sets

        // key = row or column --> 
        unordered_map<int, unordered_set<char>> rows;
        unordered_map<int , unordered_set<char>> cols;

`
        // key = [row, col] --> 

// IMPORTANT --> we need to use a map and not a unordered_map because --> IT DOES NOT SUPPORT PAIR AS A KEY 
        map<pair<int, int>, unordered_set<char>> squares;


        for (int row = 0; row < 9; row++){
            for (int col = 0; col < 9; col++){

                if (board[row][col] == '.') continue;

                pair <int, int> square_key = {row / 3, col / 3};

                // we fid if we have duplicate in any of the 3 sets
          
                if (rows[row].find(board[row][col]) != rows[row].end() || 
                cols[col].find(board[row][col]) != cols[col].end() ||
                squares[square_key].find(board[row][col]) != squares[square_key].end()
                ) return false;
 

                // else we keep on inserting in all 3 sets

                rows[row].insert (board[row][col]);
                cols[col].insert(board[row][col]);
                squares[square_key].insert(board[row][col]);

            }
        }
        return true;  
    }
};
```

# Python Code

## Approach 1:

3 maps
1 & 2 --> int, set
3 --> tuple, set
[EXPRESSION for VARIABLE(S) in ITERABLE]

base case --> '.'
calculate the square key
tuple
PRESENT --> check in all 3 maps
ABSENT --> add

```python
class Solution:
    def isValidSudoku(self, board: List[List[str]]) -> bool:
        rows = defaultdict(set)
        cols = defaultdict(set)
        squares = defaultdict(set)


        for row in range(0, 9):
            for col in range (0, 9):

                if (board[row][col] == "."): continue

                square_key = (row // 3, col //3)
                val = board[row][col]

                if(val in rows[row] or val in cols[col] or val in squares[square_key]): return False

                rows[row].add(val)
                cols[col].add(val)
                squares[square_key].add(val)

      
        return True
```
