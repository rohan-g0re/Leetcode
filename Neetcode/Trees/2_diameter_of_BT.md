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
    
    int height (TreeNode* node, int& global_max){

        // base case
        if (node == nullptr){
            return 0;
        }

        int left = height(node -> left, global_max);
        int right = height (node -> right, global_max);

        // if your diameter is better than max
        global_max = max (global_max, left + right);


        // return the best DEPTH (not diameter) till now
        return 1 + max(left, right);
    }
public:
    int diameterOfBinaryTree(TreeNode* root) {

        int global_max = -1;

        height(root, global_max);

        return global_max;
        
    }
};

```