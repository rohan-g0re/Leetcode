
## INTUITION:

1. We are comparing **2 trees in lockstep** --> so every recursive call takes a pair `(p_node, q_node)` that should "match"
2. Matching = same structure + same values --> so base cases cover structure (nulls), and then we check values
3. **ACTUAL WAY** --> spawn on corresponding children together: `(p.left, q.left)` and `(p.right, q.right)` --> AND them because ALL pairs must match

```cpp
class Solution {
public:
    bool isSameTree(TreeNode* p, TreeNode* q) {

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
        
    }
};

```