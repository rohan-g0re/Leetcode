

```cpp

class Solution {

private:

    int height (TreeNode* node){

        // base case
        if (node == nullptr){
            return 0;
        }

        int left = 1 + height(node -> left);
        int right = 1 + height(node -> right);

        return max(left, right);
    }


public:
    bool isBalanced(TreeNode* root) {

        // base case 
        if (root == nullptr) return true;

        // STEP 1: CHECK YOURSELF FOR HEIGHT 
        
        int left = height(root -> left);
        int right = height(root -> right);

        if (abs(left - right) > 1) return false;


        // STEP 2: IF YOU YOURSELF ARE GOOD THEN CHECK FOR YOUR CHILDREN AS WELL

        bool check_left = isBalanced(root -> left);
        bool check_right = isBalanced(root -> right);
        
        return ( check_left && check_right );
        
    }
};

```