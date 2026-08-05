## PREORDER Recursive

```cpp


class Solution {

    void helper (vector<int>& answer, TreeNode* node){

        if (node == nullptr){
            return;
        }
   
        // root - left - right
        answer.push_back(node->val);
        helper(answer, node->left);
        helper(answer, node->right);
    }

public:
    vector<int> preorderTraversal(TreeNode* root) {
        vector<int> answer;
        helper(answer, root);
        return answer;
    }
};
```
