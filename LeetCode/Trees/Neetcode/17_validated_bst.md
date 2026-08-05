## INTUITION:

1. Every node must lie in a **valid range** `(low, high)`
2. As we go down --> we **tighten** the range:
   - go LEFT --> `high` becomes current node's val
   - go RIGHT --> `low` becomes current node's val
3. If current node is OUTSIDE `(low, high)` --> NOT a valid BST
4. Null is always valid --> base case returns true

#### MAIN IDEA --> parent decides the bounds for children --> left child must be `< parent`, right child must be `> parent` --> and this must hold for ALL ancestors too (hence we pass the range down)

##### NOTE --> use `long` for bounds --> so that `INT_MIN` / `INT_MAX` themselves are valid node values

```cpp

class Solution {

private:

    bool dfs(TreeNode* node, long low, long high){

        // base case --> empty tree is valid
        if(node == nullptr) return true;

        // current node must be STRICTLY inside (low, high)
        if(node -> val <= low || node -> val >= high) return false;

        // explore:
        // LEFT  --> upper bound tightens to node -> val
        // RIGHT --> lower bound tightens to node -> val

        return dfs(node -> left, low, node -> val) && dfs(node -> right, node -> val, high);
    }

public:
    bool isValidBST(TreeNode* root) {

        // start with full open range
        return dfs(root, LONG_MIN, LONG_MAX);
        
    }
};
```
