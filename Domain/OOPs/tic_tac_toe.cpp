#include <bits/stdc++.h>
using namespace std;

/*

STEP 1: Requirement Questions:

Board size — fixed 3×3, or N×N? --> Lets choose NxN
How many players --> 2 players - both humans
Do X and O alternate strictly, or can a player move twice? --> Alternate, normal stuff
How does the game end? List every ending condition — there's more than one.
    1. some player wins --> horizontal or vertical or diagonal line of "N" symbols(X/O)
    2. grid is full
Does the game need to remember past games, or just play one? -> just play one



STEP 2: Write your one-paragraph description of the game in plain English. Underline the nouns. Then for each noun, apply the filter --> Does it have state that changes, or behavior of its own?


- both Players will be assigned a symbol in the beginning (X or O)
- PLayers can alternatively play their chance of putting their symbol anywhere IN THE GRID
- Game ends && a player wins if they have horizontal/vertical/diagonal set of symbols
- Game ends && it is a tie if the grid is full and there is not winning structure as per the above bullet
- If none of them - then the game continues

Nouns: 
1. Player:
    state:
        - symbol alloted

2. Game:
    bhv: features:
        - offering alternating plays
        - check after every move
        - game_driver --> this should make sure that each player gets alternating turns --> a player just makes a move on terminal but in the code, we handle it symbol

3. Grid:
    state:
        - empty grid
        - partially full
        - full
    bhv:
        - check game status: any player win, tie, grid full



###############

Guiding Documentation:

REQUIREMENTS
- Board: N x N
- Win condition: N in a row — horizontal, vertical, or diagonal
- 2 players, both human, strict alternation
- Termination, checked in this order:
    1. a player wins
    2. grid is full -> draw
  (win checked first, so a board-filling winning move counts as a win)
- Invalid move (occupied cell or out of bounds): rejected, same player re-prompted
- One game per run, no history


TYPES

enum Cell
    values: EMPTY, X, O
    why: fixed set of legal square contents; compiler rejects anything else
    note: the symbol IS the owner — no separate owner field

enum GameStatus
    values: IN_PROGRESS, X_WINS, O_WINS, DRAW
    why: four outcomes, so bool can't express it; named values beat int/char sentinels


CLASSES

1. Player
   responsibility: represents one participant and their symbol
   state:
     - symbol (Cell)
   behaviour:
     - none beyond access to symbol
   note: mostly a data holder — that's a legitimate finding, not a failure

2. Grid
   responsibility: stores the board and reports what the board currently means
   state:
     - cells        : N x N container of Cell
     - n            : board size, doubles as the win length
     - filledCells  : count of non-empty cells
   why filledCells : full-check would otherwise scan N^2 every move; derived
                     counter is cheap. Total cells NOT stored — derivable as n*n.
   behaviour:
     - place(row, col, symbol) -> bool
         false if out of bounds or already occupied
         only path that writes to cells, and the only place filledCells increments
     - status() -> GameStatus
         win check first, then full check
   access:
     - cells / filledCells private — if any other code can write cells,
       filledCells silently lies
   design note:
     - Grid owns the win check because Grid owns the cells (information expert).
       Game checking instead would mean exposing grid internals.
     - Extension point (do NOT build): if rule variants were needed, win logic
       moves to a separate strategy class.

3. Game
   responsibility: runs the game loop and enforces turn order
   state:
     - grid              (owned by value — board has no independent life)
     - players           (the two Player objects)
     - currentPlayerIndex  (0 or 1)
   behaviour:
     - drive the loop: prompt current player, attempt placement,
       re-prompt on rejection, check status after each successful move,
       stop and announce on a terminal status
     - alternate turns via modulo on player count
   design note:
     - turn ownership lives here, not in Player — "whose turn" is a fact about
       the group, not about any one member


CONSTRUCTORS
- Cell / GameStatus : none, they're values
- Player            : needs one — symbol must be supplied
- Grid              : needs one — takes n, sizes cells to n x n filled with EMPTY,
                      sets filledCells to 0. The two ints would hold garbage otherwise;
                      the container would self-construct but at the wrong size.
- Game              : needs one — takes n, builds grid, creates both players
                      with their symbols, sets currentPlayerIndex


DISPLAY
- enum Cell doesn't print directly — a small conversion (Cell -> printable char)
  is needed somewhere for board output. Decide where it lives.


BUILD ORDER (suggested)
1. enums
2. Grid: constructor + place        -> test by placing and printing
3. Grid: status, full-check only    -> test that a filled board reports DRAW
4. Grid: status, win check          -> the only real algorithm here
5. Game: constructor + loop

###############
*/




enum class Cell{
    EMPTY, 
    X, 
    O
};

enum class GameStatus{
    IN_PROGRESS,
    X_WINS,
    O_WINS,
    TIE
};

class Grid{

private:
    int n;
    vector<vector<Cell>> grid (n, vector<Cell>(n, EMPTY));
    int filled_count = 0;

public:

};


class Player{

private:

};