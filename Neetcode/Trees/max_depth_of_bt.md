

```cpp

class Solution {

// we need to do comparison with maxes at EACH NODE

private: 

    int in_rec (TreeNode* node){

        // base case
        if (node == nullptr){
            return 0;
        }

        int left = 1 + in_rec(node -> left);
        int right = 1 + in_rec(node -> right);

        return max(left, right);
    }

public:
    int maxDepth(TreeNode* root) {

        return in_rec(root);
        
    }
};

```