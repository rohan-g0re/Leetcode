## INTUITION:
1. I was initially thinking of spawning 2 dfs on children of root --> and keep swapping values --> but could not figure out the communication between those 2 recursive_call_stacks
2. **ACTUAL WAY was this --> swapping the links/edges recursively**  


```cpp
class Solution {
public:

    // --> this will be the recursion function itself

    TreeNode* invertTree(TreeNode* root) {

        // 1. base case

        if(root == nullptr) return nullptr;


        // 2. if there is node --> then swap the EDGES

        TreeNode* temp = root -> right;
        root -> right = root -> left;
        root -> left = temp;

        // 3. spawn the function on children (which is basically the new nodes)

        invertTree(root -> right);
        invertTree(root -> left);

        return root;
        
    }
};

```