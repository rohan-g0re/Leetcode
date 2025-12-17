## POSTORDER

```cpp

class Solution {

    void helper (vector<int>& answer, TreeNode* node){

        if (node == nullptr){
            return;
        }

        // left - right - root

        helper(answer, node->left);
        
        helper(answer, node->right);

        answer.push_back(node->val);
        

    }

public:
    vector<int> postorderTraversal(TreeNode* root) {


        vector<int> answer;

        helper(answer, root);

        return answer;
        
    }
};

```


## INORDER

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

## PREORDER 

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