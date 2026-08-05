## INORDER Recursive

```cpp

class Solution {

    void helper (vector<int>& answer, TreeNode* node){

        if (node == nullptr){
            return;
        }
   
        // left - root - right
        helper(answer, node->left);
        answer.push_back(node->val);
        helper(answer, node->right);
    }

public:
    vector<int> inorderTraversal(TreeNode* root) {
        vector<int> answer;
        helper(answer, root);
        return answer;
    }
};
```
