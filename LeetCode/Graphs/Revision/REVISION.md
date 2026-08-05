# Graphs

*Eight sub-patterns. The thing to understand before any of them: a grid **is** a graph — every cell is a node, and its four neighbours are its edges. You never build an adjacency list for a grid because the `delta[4][2]` array builds it on the fly. Once you accept that, most of this topic is one function (DFS or BFS over neighbours) with the interesting variation living in three places: **where you start**, **what counts as a valid neighbour**, and **how you mark something visited**. The load-bearing entries are patterns 2 and 3 — both are the same reversal of instinct, which is to stop starting from where the question points you. Code blocks are main logic only.*

---

## 1. Grid DFS — flood fill and component marking

**What it is:** stand on a cell, mark it, then recurse into its four neighbours. Everything reachable from your starting cell gets swallowed by one call; when it returns, you've consumed exactly one connected component.

**Why it works:** the marking is the algorithm. Without it you'd revisit cells forever, since every neighbour relationship is bidirectional. With it, each cell is entered once, which is what makes the whole thing `O(m·n)` no matter how tangled the shape. The real decision is *where you put the validity check*, and your notes catch this precisely: you can validate the neighbour **before** you recurse into it, or you can let every call validate **itself** at the top. Both work. Pre-checking keeps the recursion clean but repeats the bounds condition at every call site; self-checking makes the base case do all the work and lets you recurse blindly. Pick one and be consistent, because mixing them is how you end up double-checking some conditions and missing others.

**Where it shows up:** counting islands, filling regions, measuring areas — anything phrased as "connected blobs in a grid." The outer loop that restarts DFS from every unvisited cell is what counts components; the DFS itself just consumes one.

**Number of Islands** — the self-checking style: recurse blindly, let the callee reject itself. Note that marking the grid with `'2'` replaces the visited array entirely.

```cpp
// ------ ------ ----VERY IMPPPPPPP ------ ------ ------ ----
// check if the current indexes are valid or not
if (i < 0 || i >= m || j < 0 || j >= n) return;


// 1. -------BASE CASES-----> can be 0,1,2

// 1.1 IF LAND or already visited --> RETURN
if (grid[i][j] == '0' || grid[i][j] == '2') return;


// 1.2 IF VALID THEN MARK VISITED
grid[i][j] = '2';


// ------ ------ ----VERY IMPPPPPPP ------ ------ ------ ----

// 2. EXPLORE --> the correctness of indexes && validness of content will be checked in their individual recurive calls
DFS(i, j-1, grid);
DFS(i, j+1, grid);
DFS(i-1, j, grid);
DFS(i+1, j, grid);
```

- **Time:** `O(m · n)` — m, n = grid dimensions; each cell entered at most once.
- **Space:** `O(m · n)` — recursion stack in the worst case (one giant snaking island).

**Island Perimeter** — same walk, but the interesting event is *failure*. A perimeter edge exists exactly where exploration fails **because of water or the border** — not because the neighbour was already visited. That distinction is the whole problem: an already-visited land neighbour contributes nothing, and if you lump all failures together you overcount badly.

```cpp
for (int i = 0; i < 4; i++){
    int nrow = row + directions[i][0];
    int ncol = col + directions[i][1];

    // lets see - who makes it far
    // if succesful explore --> increment their count peri in us
    // WHAT IS SUCCESS? --> inbound && land && non-visited
    if(nrow >= 0 && nrow < grid.size() && ncol >= 0 && ncol < grid[0].size() &&
    grid[nrow][ncol] == 1 &&
    visited[nrow][ncol] == 0){

        peri += dfs(grid, visited, nrow, ncol);

    }

    // if failed explored --> increment peri by 1
    // MAIN LOGIC
        // --> there can be many reason of failure
        // --> we only increment if failure was due to WATER OR out of bounds
    else if(nrow < 0 || nrow >= grid.size() || ncol < 0 ||  ncol >= grid[0].size() || grid[nrow][ncol] == 0){
        peri += 1;
    }
}
```

- **Time:** `O(m · n)` — each land cell visited once, four neighbour checks each.
- **Space:** `O(m · n)` — visited grid plus recursion stack.

**Flood Fill** — one component instead of all of them, so there's no outer restart loop. The gotcha is genuine and easy to miss: if the new colour equals the old one, the recolour stops acting as a visited mark and the recursion never terminates. The guard has to sit in the driver, before the first call.

```cpp
int prev_color = image[sr][sc];

// INTERESTING CASE RIGHT HERE ----> if the target pixel already has the target color --> then NO ACTION REQUIRED
if (prev_color == color) return image;
```

```cpp
// 1.1 IF some other color OR target colour already, then --> RETURN
if (image[i][j] != prev_color) return;


// 1.2 IF prev_color THEN MARK VISITED
image[i][j] = color;
```

- **Time:** `O(m · n)` — worst case the whole image is one region.
- **Space:** `O(m · n)` — recursion stack; no visited array, the recolour marks it.

**Max Area of Island** — the BFS spelling of the same idea, counting as it goes. Worth knowing both spellings: DFS is shorter, BFS won't blow the stack on a huge grid.

```cpp
q.push({i, j});
grid[i][j] = 2;

int area = 1;

while (!q.empty()){

    int actual_row = q.front().first;
    int actual_col = q.front().second;
    q.pop();

    for (int i = 0; i < 4; i++){
        int neighbor_row = actual_row + deltarow[i];
        int neighbor_col = actual_col + deltacol[i];

        // check if indexes are valid

        if(neighbor_row >= 0 && neighbor_row < m && neighbor_col >= 0 && neighbor_col < n){

            // if 1 then update stuff

            if(grid[neighbor_row][neighbor_col] == 1){

                q.push({neighbor_row, neighbor_col});

                area++;
                grid[neighbor_row][neighbor_col] = 2;
            }
        }
    }
}
return area;
```

- **Time:** `O(m · n)` — each cell enters the queue at most once.
- **Space:** `O(m · n)` — queue can hold a large fraction of the grid.

---

## 2. Start from the goal — multi-source BFS ⭐

**What it is:** instead of running a search from each source and asking "how far to the nearest target," you push **every target into the queue at once** and let one BFS expand outward from all of them simultaneously. The first time a cell is reached, it's been reached by the nearest target, by definition.

**Why this is the pattern to internalise:** the naive framing of "nearest zero to each one" is `O((m·n)²)` — a separate search per cell. Flipping it costs nothing and collapses the whole thing to a single `O(m·n)` sweep, because BFS from a set of sources behaves exactly like BFS from a single virtual source connected to all of them. Your own note says it best — **don't always try to start from the grid; if you have a target in your head, start from there.** The other half of the pattern is the snapshot: freeze `q.size()` before draining, and one full drain equals one unit of distance, or one minute. That's the same snapshot idiom as level-order traversal on a tree, and here the level *is* the answer.

**Where it shows up:** rotting oranges, walls and gates, 01-matrix, "distance to the nearest X for every cell," and any spreading/infection simulation where you're asked how long until everything is covered.

**Rotting Oranges** — all initially-rotten cells seeded first; each snapshot drain is one minute. `fresh` is the termination signal, and the `fresh > 0` in the loop condition is what stops you counting a pointless final minute after everything has already rotted.

```cpp
while (!q.empty() && fresh > 0){

    int snapshot_time = q.size();

    for(int i = 0; i < snapshot_time; i++){

        int row = q.front().first;
        int col = q.front().second;
        q.pop();

        for (int i = 0; i < 4; i++){

            int neighbor_row = row + deltarow[i];
            int neighbor_col = col + deltacol[i];

            // validity check

            if(neighbor_row >= 0 && neighbor_row < m
            && neighbor_col >= 0 && neighbor_col < n
            && grid[neighbor_row][neighbor_col] == 1){

                // update grid - INFECT!!!

                grid[neighbor_row][neighbor_col] = 2;

                fresh--;

                // push this NEW ROTTEN ORANGE in queue

                q.push({neighbor_row, neighbor_col});
            }
        }
    }

    // ONE snapshot of queue has been dealt with and hence all the work till now is done in one unit time

    time++;
}

if (fresh == 0) return time;

return -1;
```

- **Time:** `O(m · n)` — every cell enqueued at most once across all sources.
- **Space:** `O(m · n)` — queue holds the current frontier, up to the whole grid.

**01 Matrix / Islands and Treasure** — the cleaner variant, and the detail worth stealing: with the distance grid initialised to a large value, the condition `result[neighbor] > result[current] + 1` **replaces the visited array entirely.** A cell is re-pushed only when you've genuinely improved it, and since distances only ever decrease and are bounded below, that terminates on its own. No snapshot needed either — the distance is carried in the grid rather than counted by levels.

```cpp
// Phase 1
for(int i = 0; i < m; i++){
    for(int j = 0; j < n; j++){
        if(mat[i][j] == 0){
            q.push({i, j});
            result[i][j] = 0;
        }
    }
}

// PHASE 2: processing using BFS
while(!q.empty()){
    auto [row, col] = q.front();
    q.pop();

    int delta[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};
    for(int i = 0; i < 4; i++){
        int nrow = row + delta[i][0];
        int ncol = col + delta[i][1];

        if(nrow >= 0 && nrow < m && ncol >= 0 && ncol < n &&
        result[nrow][ncol] > result[row][col] + 1){ // this optimizing condition is going to prevent us from getting into cyclic loop problem --> since every node is not going to be optimized all the time
            result[nrow][ncol] = result[row][col] + 1;
            q.push({nrow, ncol});
        }
    }
}
```

- **Time:** `O(m · n)` — amortised; a cell re-enters only on a strict improvement.
- **Space:** `O(m · n)` — result grid plus queue.

---

## 3. Start from the border — reverse the question ⭐

**What it is:** the question asks which cells are *enclosed* or *cannot escape*. Rather than testing each region for enclosure, you traverse inward from every border cell, marking everything that **can** escape. Whatever you never touched is the answer.

**Why the inversion is so much cleaner:** testing "is this region enclosed" directly means exploring it fully and proving a negative — that no cell in it touches the border — and you'd redo that per region. Coming from the border proves a positive instead, once, in a single sweep. The unvisited set falls out for free. This is the same instinct as pattern 2 (start where the answer is anchored, not where the question points), and once you've seen it in one problem you'll recognise it in all of them.

**Where it shows up:** surrounded regions, number of enclaves, pacific-atlantic water flow — and generally any grid question containing the words "surrounded," "enclosed," "cannot reach the edge," or "can reach the outside."

**Number of Enclaves** — DFS from every border land cell, then count what's still unvisited.

```cpp
// PART 1: mark 1's that are not part of the answer
// First and last columns.
for (int i = 0; i < m; i++){
    if(grid[i][0] == 1) dfs(grid, visited, i, 0);
    if(grid[i][n-1] == 1) dfs(grid, visited, i, n-1);
}

// First and last rows.
for (int i = 0; i < n; i++){
    if(grid[0][i] == 1) dfs(grid, visited, 0, i);
    if(grid[m-1][i] == 1) dfs(grid, visited, m-1, i);
}


// PART 2: count unvisited 1;
for (int i = 0; i < m; i++){
    for (int j = 0; j < n; j++){
        if (grid[i][j] == 1 && visited[i][j] != 1) counter++;
    }
}
```

- **Time:** `O(m · n)` — border seeding plus one final sweep, each cell touched a constant number of times.
- **Space:** `O(m · n)` — visited grid plus recursion stack.

**Pacific Atlantic Water Flow** — reversal plus a second twist. Water flows downhill, so tracing *backwards* from the ocean means you may only move to a neighbour that is **taller or equal**. Your note names it: the accept condition is inverted because you're walking against the flow. Two independent traversals, two visited grids, and the answer is their intersection — which is far cheaper than simulating a descent from every cell.

```cpp
visited[row][col] = true;

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
```

```cpp
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
```

- **Time:** `O(m · n)` — two sweeps, each cell visited at most once per ocean.
- **Space:** `O(m · n)` — two visited grids plus recursion stack.

---

## 4. BFS on an implicit graph

**What it is:** there's no grid and no adjacency list. The nodes are **states** — a string, a configuration, a tuple — and the edges are the legal moves that transform one state into another. You generate neighbours by applying moves rather than by looking them up.

**Why BFS specifically:** you're asked for the *fewest* moves, and BFS visits states in order of distance from the start, so the first time you reach the target you've reached it optimally. DFS gives you a path, not the shortest one. The non-negotiable part is the visited set: the move space is symmetric (turn a dial up, turn it back down), so without it you oscillate between two states forever. Your note names this trap exactly.

**Where it shows up:** word ladder, open the lock, sliding puzzles, minimum-genetic-mutation, and any "minimum number of operations to transform A into B" where the operations are enumerable.

**Open the Lock** — states are 4-digit strings, neighbours are the eight one-dial turns, snapshot counts moves. The optimisation that turns TLE into a pass is small and worth naming: the deadends live in an `unordered_set`, so rejecting one is `O(1)` instead of a linear scan of the list per neighbour.

```cpp
while(!q.empty()){

    depth++;
    int snapshot = q.size();

    // there are multiple nodes in this snapshot --> hence for each node:
    for(int i = 0; i < snapshot; i++){

        string node = q.front();
        q.pop();

        for(int posi = 0; posi < 4; posi++){
            auto [plus, minus] = stringify(posi, node);

            // if any of them matches trarget --> return snapshot
            if(plus == target || minus == target) return depth;

            // ELSE -> explore if NOT A deadend && not visited yet --> CHECK for both strings

            if(deads.find(plus) == deads.end() && visited.find(plus) == visited.end()){
                q.push(plus);
                visited.insert(plus); // since now we have completely process it
            }

            if(deads.find(minus) == deads.end() && visited.find(minus) == visited.end()){
                q.push(minus);
                visited.insert(minus); // since now we have completely process it
            }
        }
    }
}
```

The neighbour generator, and the two digit-wrap idioms worth memorising — `(d + 1) % 10` forward, `(d + 9) % 10` backward (adding 9 avoids a negative modulo):

```cpp
int digit = code[posi] - '0';
int plus_digit = (digit + 1) % 10;
int minus_digit = (digit + 9) % 10;

string plus = code;
plus[posi] = '0' + plus_digit;
```

- **Time:** `O(10⁴ · 4)` — 10⁴ possible states, 8 neighbours generated per state, `O(1)` set lookups.
- **Space:** `O(10⁴)` — visited set and queue over the state space.

---

## 5. Topological sort — Kahn's algorithm

**What it is:** count how many prerequisites each node has (its **indegree**), queue everything with zero, and repeatedly remove a node and decrement its dependents. Anything that reaches zero joins the queue.

**Why it detects cycles for free:** a node inside a cycle always has at least one unsatisfied prerequisite — another node in the same cycle — so its indegree never drops to zero and it never enters the queue. That means the count of processed nodes tells you everything: process all of them and the graph is acyclic; fall short and the leftovers are exactly the cycle. You get ordering and cycle detection out of one loop. The efficiency detail your comment flags is real — after removing a node you only re-check the indegrees of *its* dependents, never the whole array.

**Where it shows up:** course schedule, build/dependency ordering, alien dictionary, task scheduling with prerequisites. The tell is "before/after" or "depends on."

**Course Schedule I & II** — one skeleton, two endings. Note the edge direction: `pair[1]` is the prerequisite and points *to* `pair[0]`, whose indegree goes up.

```cpp
// STEP 1: add in indegree array & an adj list
for(auto& pair : prereq){
    in_degree [ pair[0] ]++;
    adjlist[pair[1]].push_back(pair[0]);
}

// STEP 2: push all indegree = 0 nodes into queue
for (int i = 0; i < numCourses; i++){
    if (in_degree[i] == 0){
        q.push(i);
    }
}

// STEP 3: LOOP BABY
while (!q.empty()){

    // 3.1 pop a node and add in result
    int node = q.front();
    q.pop();
    result.push_back(node);

    // 3.2 check all the outgoing nodes fron the "NODE" and decrement their in-degree values
    for(auto v : adjlist[node]) {
        in_degree[v]--;

        // 3.3 IS THERE ANY in-degree == 0?
        // since we made changes(decrements) to only "NODE"'s destinations -- therefore we can only check if "THEY" have reached zero
        // IMPORTANT --> WE DONT HAVE TO CHECK EVERYTHING
        if(in_degree[v] == 0){
            q.push(v);
        }
    }
}

// STEP 4: Check the final sorted order
if (result.size() == numCourses) return result;
return {};
```

*(Course Schedule I is this with `result` replaced by a `counter` — `counter == numCourses` means no cycle, so the schedule is finishable.)*

- **Time:** `O(V + E)` — V = courses, E = prerequisite pairs; each edge decremented once.
- **Space:** `O(V + E)` — adjacency list, indegree array, and queue.

---

## 6. Connected components — restart from every unvisited node

**What it is:** an outer loop over all nodes; whenever you find one that hasn't been visited, increment a counter and launch a traversal that consumes its entire component. The traversal doesn't count anything — the *restart* is the count.

**Why the outer loop is non-negotiable:** a single traversal only reaches what's reachable, so on a disconnected graph one call sees one component and reports a wrong answer. Your note connects it correctly — this is islands and provinces wearing different clothes; the only thing that changes is how you enumerate neighbours.

**Where it shows up:** counting components, number of provinces, validating a tree, friend circles, and as the outer scaffold of every grid-island problem in pattern 1.

**Count Components** — the canonical shape: restart, count, consume.

```cpp
for (int i = 0; i < n; i++) {

    // if un-visited --> explore
    if (visited[i] == 0){
        components++;
        dfs(adj, visited, i);
    }
}
```

- **Time:** `O(V + E)` — V = nodes, E = edges; each visited once across all restarts.
- **Space:** `O(V + E)` — adjacency list plus visited array and recursion stack.

**Number of Provinces** — the same pattern over an **adjacency matrix**, which is the point of the exercise. Finding neighbours means scanning an entire row rather than walking an edge list, so the cost per node is `O(n)` regardless of how few edges there actually are.

```cpp
for (int i = 0; i < n; i++){

    if (visited[i] != 1){

        provinces++;

        queue <int> q;
        q.push(i);

        while (!q.empty()){
            int node = q.front();
            q.pop();

            // find neighbors
            for (int col = 0; col < n; col++){

                    // is neighbor                  not visited
                if (isConnected[node][col] == 1 && visited[col] != 1){

                    q.push(col);
                    visited[col] = 1;
                }
            }
        }
    }
}
```

- **Time:** `O(n²)` — n = cities; the matrix forces a full row scan per node.
- **Space:** `O(n)` — visited array and queue (the matrix is given, not built).

**Graph Valid Tree** — a tree is a connected, acyclic graph, so you check both. Cycle detection on an *undirected* graph needs the parent check: seeing a visited neighbour is normal if it's the node you just came from, and a cycle only if it isn't. Then the final scan catches disconnection, which is the half people forget — an acyclic but disconnected graph is a forest, not a tree.

```cpp
// 2. check for neighbors
for (auto neighbor : adj_list[node]){

    // 2.1. Oh my god, the neighbor is visited.
    if (visited[neighbor] == 1){

        // 2.1.1 If the visited guy is not the parent, then it's done. It's a cycle.
        if (neighbor != parent) return false;

        // 2.1.2. If it's visited and it's not 2.1.1, then it is basically a parent, so don't do anything else, continue to the next neighbor.
        continue;
    }

    // 2.2. not visited
    visited [ neighbor ] = 1;
    q.push({neighbor, node});
}

// IMPORTANT CASE 2 - if the graph is disconnected, then it's not a valid tree. So, check if everyone is visited.
for (auto num: visited){
    if (num == 0) return false;
}
```

*One thing to fix before you rely on this: in the DFS version of the same file, the recursive call's return value is never checked, so a `false` found deep in the recursion is silently dropped. The BFS version above doesn't have that problem — prefer it, or propagate the result in the DFS with `if (!dfs_rec(...)) return false;`.*

- **Time:** `O(V + E)` — V = nodes, E = edges; one BFS plus one final scan.
- **Space:** `O(V + E)` — adjacency list, visited array, queue.

**Course Schedule IV** — reachability, not ordering, and your notes record exactly why the obvious idea fails. A topological order puts `a` before `b` even when there's no path between them at all, so topo order can't answer "is `a` a prerequisite of `b`." What you need is a reachability matrix: run a DFS from every node, marking everything it can reach.

```cpp
// find neighbors
for(auto neighbor : adjlist[node]){
    // traverse if NOT visited
    if (reach[source][neighbor] != 1){

        // mark visited from source but traverse on the next neighbor

        reach[source][neighbor] = 1;
        rec_dfs(adjlist, reach, source, neighbor);
    }
}
```

```cpp
// the driver is based upon the question that -- the name of courses are basically from 0 to numcourses-1
for (int i = 0; i < numCourses; i++){
    rec_dfs(adjlist, reach, i, i);
}
```

- **Time:** `O(V · (V + E))` — one full DFS per source node.
- **Space:** `O(V²)` — the reachability matrix dominates.

---

## 7. Clone with a hash map

**What it is:** copying a graph node by node, with a `original → clone` map that doubles as the visited set. Look up before you build; if the clone already exists, return it instead of making another.

**Why the map has to be written before the recursion:** the moment you recurse into a neighbour, that neighbour may recurse straight back to you — graphs have cycles. If your own clone isn't in the map yet when that happens, you build a second copy of yourself and the recursion never bottoms out. Inserting `visited[node] = clone` *before* the neighbour loop is what breaks the cycle. This is the same trick as the linked-list copy with random pointers: the map is simultaneously "have I seen this" and "what did it become."

**Where it shows up:** clone graph, deep-copying any structure with shared or cyclic references, and memoising a recursion whose state is a pointer rather than an index.

**Clone Graph** — insert into the map first, recurse second.

```cpp
// 1. BASE CASES

// 1.1 reached leaf node
if (node == nullptr) return nullptr;

// 1.2 node already created
if (visited.find(node) != visited.end())return visited[node];


// 2. RECURSION LOGIC

Node* clone = new Node (node->val);
// CLONING VALUE: we create a BRAND NEW node with the same value as the one to be cloned

// But still the neighbor list is remaining --> we do that by going in depth and creating that node first and then it will get added to this node's neighbor list

visited[node] = clone;

// CLONING NEIGHBOR
for (auto neighbor : node -> neighbors){

    clone->neighbors.push_back(cloneGraph(neighbor));

}

return clone;
```

- **Time:** `O(V + E)` — V = nodes, E = edges; every node cloned once, every edge followed once.
- **Space:** `O(V)` — the map plus recursion stack.

---

## 8. Degree counting — the graph you never traverse

**What it is:** problems that hand you edges and ask a question answerable purely from **how many** edges touch each node. No queue, no recursion, no visited array.

**Why it deserves its own slot:** the instinct on seeing a list of edges is to build an adjacency list and search, and that instinct is wrong here — it costs you time and code for information you never use. If the property you're checking is a local degree condition, counting is the entire solution. Recognising when *not* to traverse is a real skill.

**Where it shows up:** find the town judge, "the one node everyone points to," and quick structural sanity checks (a tree on n nodes has exactly n−1 edges).

**Find the Town Judge** — the judge is trusted by everyone else and trusts nobody: indegree n−1, outdegree 0. The optimisation is the neat part — combine both counters into one signed array, since only the judge can possibly net out to n−1.

```cpp
for (auto pair : trust){
    optimal[pair[1]]++; // Represents the in_degree being added
    optimal[pair[0]]--; // Represents the out_degree being subtracted
}

for (int i = 1; i < n+1; i++){
    if (optimal[i] == n-1) return i;
}
```

- **Time:** `O(E + n)` — E = trust pairs, n = people; two linear passes.
- **Space:** `O(n)` — one counter array, sized `n+1` to skip zero-index juggling.

**Verifying an Alien Dictionary** — filed under graphs by association only; **this one has no graph in it at all.** The order is given as a string, so you build a `char → rank` map and do a pairwise prefix comparison. The subtle case is the last check: if one word is a prefix of the next and is *longer*, the ordering is invalid even though no character ever mismatched.

```cpp
while(p < s1.size() && p < s2.size()){

    // not a match --> check
    if(s1[p] != s2[p]){

        // good match
        if(mp[s1[p]] < mp[s2[p]]) {
            found  = true;
            break;
        }
        // bad match
        else{
            return false;
        }
    }

    // else - no match
    p++;
}

if(found == false && s1.size() > s2.size()) return false;
```

- **Time:** `O(total characters)` — every character compared at most once across all adjacent pairs.
- **Space:** `O(1)` — the rank map is a fixed 26 entries.

**Still open in this topic:** *Redundant Connection is unfinished. Your DFS attempt is in the file with your own note explaining why it fails — the edge that closes a cycle is not necessarily the last edge added, so finding the cycle doesn't identify the right edge to remove. The correct answer is union-find: process edges in order and return the first one whose two endpoints already share a root. That's the only union-find problem in this set, and it's worth writing, because union-find also gives you a second solution to components, provinces, and valid-tree.*

---

*Threads out of this topic: patterns 2 and 3 are the same move — **anchor the search where the answer is, not where the question points.** Multi-source BFS starts at the targets; border traversal starts at the escape route. The **snapshot** that counts minutes in pattern 2 is the identical idiom that counts levels in Trees, because a BFS level and a unit of time are the same thing. And the hash map in pattern 7 is the same original-to-copy map used in Linked Lists — "have I seen this" and "what did it become," on one lookup.*
