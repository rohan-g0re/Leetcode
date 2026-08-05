```bash

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

```

```cpp

class Solution {

// we need to do comparison with maxes at EACH NODE

private: 

    int rec_inorder (TreeNode* node){

        // base case
        if (node == nullptr){
            return 0;
        }

        int left = 1 + rec_inorder(node -> left);
        int right = 1 + rec_inorder(node -> right);

        return max(left, right);
    }

public:
    int maxDepth(TreeNode* root) {

        return rec_inorder(root);
    }
};

```