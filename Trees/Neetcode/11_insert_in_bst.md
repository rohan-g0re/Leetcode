## INTUITION:

- recurse till bottom
- need to use dfs(postorder/preorder)
- explore wrt target
- when reached to null --> call constructor - and add the node

# 2 Main Intuitions:

### 1. As we are exploring based on target value --> **WE CANT REACH ANY OTHER NULL NODE**

### 2. if we reach null node and then create then we cant link --> hence we need to CHECK BEFORE EXPLORING --> **Insert node when we are on LEAF NODE**

```cpp

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */

class Solution {
private:
    void dfs(TreeNode* root, int val){

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

        return;
    }


public:
    TreeNode* insertIntoBST(TreeNode* root, int val) {

        // base case --> empty tree
        if(root == nullptr){
            root = new TreeNode(val);
            return root;
        }

        dfs(root, val);
        return root;
    }
};
```
