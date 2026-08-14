# Trees

*Seven sub-patterns, and almost all of them are the same three lines of code with a different thing happening in the middle. A tree question is never really "how do I traverse" — you already know that. It's **what information moves, and in which direction.** Something goes down (bounds, a running max, a depth), something comes back up (a height, a boolean, a count), and occasionally something sits outside the recursion entirely and gets written to. Once you can name those three channels, every problem here collapses into "which channels does this one use." The load-bearing entry is pattern 4 — the one where a function returns one thing but answers another. Code blocks are main logic only.*

---

## 1. Traversal order — where the visit sits

**What it is:** the three-line recursion `go left / visit / go right`, where moving the `visit` line changes which order the nodes come out in. Inorder puts it in the middle, preorder at the top, postorder at the bottom. That's the entire difference.

**Why it works:** recursion already walks the whole tree; the only free choice you have is *when* you record the current node relative to descending into its children. Preorder records before you know anything about the subtrees, postorder records only after both are finished — which is why postorder is the natural home for anything that needs its children's answers first. The iterative versions exist because an interviewer may ask you to prove you understand what the call stack was doing for you: you push left-spine nodes onto an explicit stack, then peel them off.

**Where it shows up:** as the skeleton of literally everything else in this document. Also directly, when a problem needs a specific output order, and — critically — when the tree is a BST, because **inorder on a BST comes out sorted.** That one fact turns several BST problems into array problems.

**Inorder / Preorder / Postorder** — the same recursion, the visit line moved.

```cpp
if (node == nullptr){
    return;
}

// left - root - right
helper(answer, node->left);
answer.push_back(node->val);
helper(answer, node->right);
```

```cpp
// root - left - right
answer.push_back(node->val);
helper(answer, node->left);
helper(answer, node->right);
```

```cpp
// left - right - root
helper(answer, node->left);
helper(answer, node->right);
answer.push_back(node->val);
```

- **Time:** `O(n)` — n = number of nodes; every node visited exactly once.
- **Space:** `O(h)` — h = height of tree, the recursion stack; `O(n)` on a skewed tree.

**Postorder, iterative** — the hard one of the three, and the reason is worth knowing. Postorder needs to visit a node *after* its right subtree, so when you come back up to a node you have to be able to tell "have I already done your right side?" The `lastvisited` pointer is that memory. Without it you descend right, come back, see a right child again, and loop forever.

```cpp
while (!st.empty() || current != nullptr){

    // recursively go traverse left until you ARE A NULL NODE

    while ( current != nullptr ){
        st.push(current);
        current = current -> left;
    }

    // help me!!! - somebody from stack --> SO YOU PEEK

    TreeNode* peek = st.top();

    // NOW 2 cases:

    // 2.1 if the peeked node has right child && it has not been visited yet --> traverse right node

    if (peek -> right != nullptr && peek -> right != lastvisited){
        current = peek -> right;
    }

    // 2.2 it does not have a right child or else it was PROCESSED earlier --> then it means you dont have anything left --> HENCE, PRINT & PROCESS IT;

    else{
        result.push_back(peek -> val);
        lastvisited = peek; // (can also be st.top() itself) we are doing this bcoz once printed - we dont want the parent to come again this path


// THIS ALSO GETS CHECKED IN CASE 2.1 -- where we are checking if the right node that you are talking about is not the one already done - or else it would be an infinite loop (process right child - comebackup - "OOHH we still have a right child" :DUMB:)

        st.pop();
    }
}
```

- **Time:** `O(n)` — each node is pushed once and popped once.
- **Space:** `O(h)` — explicit stack holds one root-to-node path at a time.

**Kth Smallest in BST** — iterative inorder with an early exit. The twist is that there's no clever algorithm here at all; the insight is the one-liner the file opens with, that inorder on a BST *is* sorted order, so you just count off k nodes and stop. Simpler than postorder because there's no come-back-to-me case: once you pop a node you're immediately done with it and move right.

```cpp
while (current != nullptr || !st.empty()){

    // STEP 1: traverse in depth in left

    while (current != nullptr){
        st.push(current);
        current = current -> left;
    }

    // STEP 2.1: now we are on null --> PEEK and get the top node from stack

    TreeNode* peek = st.top();
    st.pop();

    // STEP 2.2: register this peeked node

    counter++;
    if (counter == k) return peek -> val;

    // STEP 3: we move to right
    current = peek -> right;
}
```

- **Time:** `O(h + k)` — h = height to reach the smallest, then k pops; not full `O(n)` thanks to the early return.
- **Space:** `O(h)` — stack only ever holds the current left spine.

---

## 2. Return a value up — post-order aggregation

**What it is:** the child calls run first, and the current node combines their two answers into one answer for itself. Nothing is passed down; everything flows upward.

**Why it works:** by the time the two recursive calls return, the entire subtree below you has been reduced to a single number or boolean, and you never have to look at it again. That's the whole appeal — the current node only ever holds two values regardless of how big the subtree was. The shape is always the same: base case for `nullptr`, two recursive calls, one combining line, one return.

**Where it shows up:** heights, depths, sizes, counts, and any yes/no property that is true for a node exactly when it's true for both children. If you can phrase the question as "what does my left subtree tell me and what does my right subtree tell me," you're here.

**Maximum Depth** — the archetype. Two calls, take the max, add one for yourself.

```cpp
// we need to do comparison with maxes at EACH NODE

// base case
if (node == nullptr){
    return 0;
}

int left = 1 + rec_inorder(node -> left);
int right = 1 + rec_inorder(node -> right);

return max(left, right);
```

- **Time:** `O(n)` — n = nodes; every node contributes one constant-work frame.
- **Space:** `O(h)` — h = height, recursion stack depth.

**Balanced Binary Tree** — worth flagging honestly: **this version is the brute force.** It computes `height()` from scratch at every node, so the height work is redone all the way down and you pay `O(n²)` on a skewed tree. The optimal fuses the two recursions — have `height()` return `-1` as a poison value the moment it detects imbalance, and the whole check becomes a single pass. Interviewers ask for that fusion specifically, so know that this is the version to *start* from and improve.

```cpp
// base case
if (root == nullptr) return true;

// STEP 1: CHECK YOURSELF FOR HEIGHT

int left = height(root -> left);
int right = height(root -> right);

if (abs(left - right) > 1) return false;


// STEP 2: IF YOU YOURSELF ARE GOOD THEN CHECK FOR YOUR CHILDREN AS WELL

// THIS IS VERY IMPORTANT AS THIS IS THE WAY WE MAKE SURE THAT WE CHECK RECURSIVELY FOR ALL THE CHILDREN NODES

bool check_left = isBalanced(root -> left);
bool check_right = isBalanced(root -> right);

return ( check_left && check_right );
```

- **Time:** `O(n²)` — n = nodes; height recomputed per node (optimal fused version is `O(n)`).
- **Space:** `O(h)` — h = height, recursion stack.

**Construct Quad Tree** — the same upward flow, except what comes back up is a *node* rather than a number. Every call builds its own node unconditionally and only attaches children if the region turned out to be mixed. The twist is that `verify` returns a `pair<bool,bool>` — value and is-leaf together — because a single bool can't distinguish "all ones" from "not uniform."

```cpp
auto pair = verify(grid, row1, row2, col1, col2);
bool val = pair.first;
bool leaf = pair.second;

Node* node = new Node(val, leaf);

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
```

- **Time:** `O(n² log n)` — n = grid side; each of the log n levels re-scans up to the whole grid in `verify`.
- **Space:** `O(log n)` — recursion depth; output tree excluded.

---

## 3. Carry state down — the parent decides the child's rules

**What it is:** the recursive call takes extra parameters that encode what the ancestors have already decided — a valid range, a running maximum, a target value. The child's behaviour depends on what it was handed.

**Why it works:** some properties simply aren't local. A node's value being less than its parent doesn't make it a valid BST node — it has to be inside the range carved out by *every* ancestor above it. Passing the range down is how you make a global constraint checkable locally, and it's why this pattern exists at all. Each call narrows the window a little more, and the narrowing is the algorithm.

**Where it shows up:** validation against ancestors, "compared to everything above me" questions, and BST descent where the value you're looking for tells you which way to go. If a naive local check gives the wrong answer on a deep counterexample, you need to be carrying state down.

**Validate BST** — the range tightens on the way down: going left caps the ceiling at the parent, going right raises the floor. The practitioner's detail is `long` for the bounds — with `int`, a node legitimately holding `INT_MIN` collides with your sentinel and gets rejected.

```cpp
// base case --> empty tree is valid
if(node == nullptr) return true;

// current node must be STRICTLY inside (low, high)
if(node -> val <= low || node -> val >= high) return false;

// explore:
// LEFT  --> upper bound tightens to node -> val
// RIGHT --> lower bound tightens to node -> val

return dfs(node -> left, low, node -> val) && dfs(node -> right, node -> val, high);
```

- **Time:** `O(n)` — n = nodes; each visited once with `O(1)` bound checks.
- **Space:** `O(h)` — h = height, recursion stack.

**Count Good Nodes** — a hybrid, and a good one to understand: `curr_max` travels **down** (each child gets its ancestors' maximum) while `count` is summed **up** from the children. Two directions in one function. Your own note flags the alternative — a reference-passed global counter — which trades the summing-up channel for a side-channel, landing you in pattern 4.

```cpp
// base case
if(node == nullptr) return 0;

//logic
// good node when val is more than max

int count = 0;

if(curr_max <= node -> val){
    count++;
    curr_max = node -> val;
}

// explore
count += dfs(node -> left, curr_max);
count += dfs(node -> right, curr_max);

return count;
```

- **Time:** `O(n)` — n = nodes; one constant-work visit each.
- **Space:** `O(h)` — h = height; `curr_max` is passed by value, no extra structure.

---

## 4. Return one thing, answer another — the side-channel ⭐

**What it is:** the function returns the value its *parent* needs, while the value *you* actually want gets written to a reference passed through every call. Two separate pieces of knowledge, travelling on two separate channels.

**Why this is the pattern to get right:** the trap in diameter is trying to return the diameter. You can't — your parent doesn't need your diameter, it needs your height, because that's what it will use to compute *its own* diameter. But the answer is a diameter. The resolution is to stop treating "what I return" and "what I'm computing" as the same thing. Your own notes call it exactly right: the height is the **local knowledge to be returned**, and the max is the answer, updated on the side. Once you internalise that split, a whole class of "best path/value anywhere in the tree" problems becomes routine — you ask "what does my parent need from me?" and return that, then update the global separately.

**Where it shows up:** diameter, maximum path sum, longest univalue path, largest BST subtree — anything phrased as "the best X *anywhere* in the tree," where the best answer might live entirely inside a subtree and never involve the root. And in a different guise, any traversal where arrival order itself is the information.

**Diameter of Binary Tree** — the canonical two-channel function. Note it returns `1 + max(left, right)` and never returns `global_max` at all.

```cpp
// base case
if (node == nullptr){
    return 0;
}

int left = height(node -> left, global_max);
int right = height (node -> right, global_max);

// if your diameter is better than max
global_max = max (global_max, left + right);


// return the best DEPTH (not diameter) till now + 1 BCOZ you also need to add the root as a node in the path
return 1 + max(left, right);
```

- **Time:** `O(n)` — n = nodes; single pass, height computed once per node.
- **Space:** `O(h)` — h = height, recursion stack; `global_max` is a single int.

**Right Side View** — the side-channel is `max_height`, and the clever part is that the *traversal order* carries the logic. Go right before left, and the first node you ever reach at a new depth is by definition the rightmost one at that depth. No level-order machinery needed; the ordering does the work. Most people solve this with BFS — solving it with DFS and explaining why right-first is sufficient is the better answer.

```cpp
curr_height += 1; // increment height as this is a new node

if(curr_height > max_height){
    result.push_back(root -> val); // this depth is first time seen as any node here is to be added to result
    max_height = curr_height;       // this is the new max depth
}

// explore --> right first

if(root -> right != nullptr) dfs(root -> right, result, curr_height, max_height);
if(root -> left != nullptr) dfs(root -> left, result, curr_height, max_height);
```

- **Time:** `O(n)` — n = nodes; every node visited once regardless of order.
- **Space:** `O(h)` — h = height, recursion stack; output excluded.

---

## 5. BFS by level — the snapshot

**What it is:** a queue-based sweep where, before processing, you record `q.size()` — freezing how many nodes belong to the current level — and then process exactly that many. Anything pushed during those iterations belongs to the *next* level.

**Why the snapshot is the whole trick:** the queue is constantly growing as you push children, so "process until the queue is empty" gives you a flat stream with no level boundaries. Taking the size first draws a line: those n nodes are this level, everything after is not. It costs one integer and it's the difference between a traversal and a level-order traversal. **This exact snapshot idiom reappears in graphs** — it's how rotting-oranges counts minutes and how open-the-lock counts turns, because "one level" and "one unit of time" are the same thing.

**Where it shows up:** level-order output, "nodes at each depth," minimum depth (BFS finds it first and you stop), zigzag order, and any question where the answer is per-level rather than per-node.

**Level Order Traversal** — snapshot, drain exactly that many, push children as you go.

```cpp
q.push(root);

while (!q.empty()){

    int snapshot = q.size();

    vector <int> level;

    for (int i = 0; i < snapshot; i++){

        TreeNode* node = q.front();
        level.push_back(node->val);

        q.pop();
        if (node -> left != nullptr) q.push(node -> left);
        if (node -> right != nullptr) q.push(node -> right);

    }

    result.push_back(level);

}
```

- **Time:** `O(n)` — n = nodes; each enters and leaves the queue once.
- **Space:** `O(w)` — w = maximum width of the tree, the widest level in the queue; up to `n/2`.

---

## 6. Two trees in lockstep — structural comparison

**What it is:** the recursion takes a *pair* of nodes rather than one, and descends both trees together — left with left, right with right — ANDing the results.

**Why the base cases carry the weight:** structure and values are two different failure modes, and the null checks are what separate them. Both null means these positions agree and you're done. Exactly one null means the shapes differ — and note this check must come *after* the both-null check, or you'd reject a matching pair of empty subtrees. Only once structure is settled do you compare values. Get that ordering wrong and the function is subtly broken on trees that differ in shape.

**Where it shows up:** same tree, symmetric tree (the mirror variant, where you pair left-with-right instead), subtree checks, and merging two trees.

**Same Tree** — three base cases in a deliberate order, then descend both trees together.

```cpp
// ------ BASE CASES ------

// 1. if both are null --> same tree
if( p == nullptr && q == nullptr) return true;

// 2. if one of them is null --> FAILED MATCH
if( p == nullptr || q == nullptr) return false;
// TECHNICALLY this could execute even if both are nulls --> but we ended up here bcoz first base case did not execute

// 3. if values mismatch --> FAILED
if( p -> val != q -> val) return false;


// ----- MAIN LOGIC -----

// the function compares 2 nodes --> therefore we need to spawn on left child of p and q together -- and on right child of p and q as well

return (isSameTree( p -> left, q -> left) && isSameTree( p -> right, q -> right));

// we "AND" it because --> we return true if Both subtrees match
```

- **Time:** `O(min(n, m))` — n, m = node counts; stops at the first mismatch.
- **Space:** `O(min(h1, h2))` — recursion depth, bounded by the shallower tree.

**Subtree of Another Tree** — `same_tree` wrapped in a traversal. At every node of the big tree you ask "does a full match start here?" The OR is the counterpart to the AND above: a match anywhere is enough.

```cpp
if(root == nullptr) return false;

// 1. match --> spawn
if(root -> val == subroot -> val){
    if(same_tree(root, subroot)){
        return true;
    }
}

// 2. no match --> explore children
return (preorder(root -> left, subroot) || preorder(root -> right, subroot) );

// "OR" because we return true if there was a macth in either of the sub-trees
```

The optimal version is a different idea entirely — serialize both trees into strings and ask whether one contains the other, turning a tree problem into substring search. The detail that makes it correct is the `N` null marker: without markers, two differently-shaped trees can serialize identically, and you'd report a match that isn't there.

```cpp
if (!node) return "N";
return "(" + to_string(node->val) + "," + serialize(node->left) + "," + serialize(node->right) + ")";
```

- **Time:** `O(n × m)` brute → `O(n + m)` serialized — n = main tree nodes, m = subtree nodes.
- **Space:** `O(h)` brute → `O(n + m)` serialized — the serialized strings dominate.

---

## 7. BST property and structural mutation

**What it is:** two related habits. First, using the ordering property to prune — a value comparison tells you which single child to descend into, so you pay `O(h)` instead of `O(n)`. Second, actually rewiring the tree: relinking pointers rather than just reading them.

**Why pruning works, and where it stops:** in a BST every value in the left subtree is smaller and every value on the right is larger, so one comparison eliminates an entire side. That's the same halving argument as binary search, and it's why BST operations are height-bound. But it only applies when the ordering is meaningful — LCA on a *general* binary tree has no such property, so you must recurse into both sides and reason about what comes back. The two LCA solutions side by side are the cleanest illustration in this document of what the BST property actually buys you.

**Where it shows up:** search, insert, delete, LCA, floor/ceiling, and range queries on BSTs — plus in-place restructuring like inverting a tree.

**Lowest Common Ancestor — general binary tree.** No ordering to exploit, so recurse both sides and read the returns: two non-null answers means the two targets split here, and this node is the meeting point.

```cpp
// base case
if (root == NULL || root == p || root == q){
    return root;
}

// recurse both sides

TreeNode* left = lowestCommonAncestor(root -> left, p, q);
TreeNode* right = lowestCommonAncestor(root -> right, p, q);


// return logic

if (left == NULL){
    return right; // Both found in right, or only right found
}
else if (right == NULL){
    return left; // Both found in left, or only left found
}
else{
    // handles the case where both are NOT null --> which means that both are on subtrees below

    // in such case we need the root itself bcoz this would SURELY BE THE FIRST TIME THIS HAS HAPPENED -->
    // which means this root is the actual answer

    return root;
}
```

**Lowest Common Ancestor — BST.** Same problem, but one comparison per node picks a single direction. The `else` branch is the answer: the moment the current value sits between the two targets, they've split, and you're standing on the LCA.

```cpp
if (root == NULL) return NULL;

// dont need to search the right subtree
if (root -> val > max (p -> val, q -> val)){
    return lowestCommonAncestor(root -> left, p, q);
}

// dont need to search the left subtree
else if (root -> val < min (p -> val, q -> val)){
    return lowestCommonAncestor(root -> right, p, q);
}
else{
    /*
    Handles 2 cases:
        1. Root matched to one of the P or Q nodes
            --> which means the other one is the child
            --> which means that this node is LCA

        2. Root -> val is in BETWEEN P and Q
            --> this means that p and q are no more on one side together
            --> which means that p and q are in left and right subtree respectively
            --> this can only happen if the current root is AN IMMEDIATE PARENT OF BOTH p and q
            --> hence current node is the Least Common Ancestor
    */

    return root;
}
```

- **Time:** `O(n)` general tree → `O(h)` BST — n = nodes, h = height; the ordering property is what buys the difference.
- **Space:** `O(h)` — recursion stack in both versions.

**Insert into a BST** — descends by comparison, but with a look-ahead: it checks whether the next node exists *before* recursing, so it stops standing on the leaf and can attach the new node. Your note names the reason exactly — recurse into the null and you've lost the parent you needed to link to.

```cpp
// we can traverse --> hence leaf node not reached

if(val > root -> val && root -> right != nullptr){
    dfs(root -> right, val);
    return;
}
else if(val < root -> val && root -> left != nullptr) {
    dfs(root -> left, val);
    return;
}

// leaf node reached --> as the next node is nullptr
TreeNode* node = new TreeNode(val);
if(val < root -> val){
    root -> left = node;
}
else{
    root -> right = node;
}
```

- **Time:** `O(h)` — h = height; one comparison per level, no backtracking.
- **Space:** `O(h)` — recursion stack; `O(1)` if written as a loop.

**Delete from a BST** — the hardest one here, and the mechanism is the thing to remember. Everything is passed as `TreeNode*&` — a **reference to a pointer** — so assigning `node = node->left` inside the function rewires the *parent's* child pointer directly. That's what removes the usual "return the new subtree and reattach it at every call site" boilerplate. The deletion strategy itself: replace the node's value with its inorder successor, then delete the successor — which is easy, because a successor is the leftmost node of the right subtree and therefore has no left child, so splicing in its right subtree (possibly null) always works.

```cpp
int successor(TreeNode*& root){

    if(root -> left != nullptr) {
        return successor(root -> left);
    }

    // gottcha here --> found the successor

    // 1. store value
    int succ = root -> val;

    // 2. delete node: BY SETTING IT AS RIGHT SUBTREE
    root = root -> right;

    // 3. return value
    return succ;
}
```

```cpp
// 2 --> if match
if(node -> val == key){

    // 2.1 if right exists --> replace with smallest successor

    if(node -> right != nullptr){
        // find succ && delete succ && return succ value
        int succ = successor(node -> right);
        node -> val = succ;
    }

    // 2.2 if right does not exist --> just link directly to left node
    else{
        if(node -> left == nullptr){
            node = nullptr;
            return;
        }
        else{
            node = node -> left; // should handle null nodes as well
        }
    }

    return;
}

// 3. if not --> then explore wrt BST properties
else{
    if(node -> val > key){
        dfs(node -> left, key);
    }
    else{
        dfs(node -> right, key);
    }
}
```

- **Time:** `O(h)` — h = height; one descent to find the key, one more to find its successor.
- **Space:** `O(h)` — recursion stack.

**Invert Binary Tree** — mutation without any BST ordering involved. Your own note records the wrong turn worth remembering: the instinct is to swap *values* across two parallel recursions, and the two call stacks have no way to talk to each other. Swapping the **links** at each node makes the problem trivially local.

```cpp
// 1. base case

if(root == nullptr) return nullptr;


// 2. if there is node --> then swap the EDGES

TreeNode* temp = root -> right;
root -> right = root -> left;
root -> left = temp;

// 3. spawn the function on children (which is basically the new nodes)

invertTree(root -> right);
invertTree(root -> left);
```

- **Time:** `O(n)` — n = nodes; one constant-time swap each.
- **Space:** `O(h)` — h = height, recursion stack.

---

*Threads out of this topic: the **side-channel** of pattern 4 — return what your parent needs, write the answer elsewhere — is the tree version of the same "don't recompute what you can carry" instinct behind the monotonic stack and the never-decreasing `maxf` in the sliding window. The **snapshot BFS** of pattern 5 is the identical idiom you use in Graphs for rotting oranges and open-the-lock, where a level is a unit of time. And the BST pruning in pattern 7 is Binary Search wearing pointers instead of indices — one comparison, half the space gone.*
