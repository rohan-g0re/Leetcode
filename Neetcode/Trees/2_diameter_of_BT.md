```cpp

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


        // return the best DEPTH (not diameter) till now + 1 BCOZ you also need to add the root as a node in the path
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