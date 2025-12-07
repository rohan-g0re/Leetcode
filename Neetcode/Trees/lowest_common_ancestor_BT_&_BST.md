## BINARY TREE 

```cpp

class Solution {
public:
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {

        // base case

        if (root == NULL || root == p || root == q){
            return root;
        }

        // recurse both sides

        TreeNode* left = lowestCommonAncestor(root -> left, p, q);

        TreeNode* right = lowestCommonAncestor(root -> right, p, q);


        // return logic

        if (left == NULL){
            return right; // Both found in right, or only right found
        }
        else if (right == NULL){
            return left; // Both found in left, or only left found  
        }
        else{
            // handles both cases --> 
            //     1. left and right null
            //     2. both NOT null

            return root;
        }


        
    }
};

```

## BINARY SEARCH TREE

```cpp

class Solution {
public:
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {

        if (root == NULL) return NULL; 

        if (root -> val > max (p -> val, q -> val)){
            return lowestCommonAncestor(root -> left, p, q);
        }
        else if (root -> val < min (p -> val, q -> val)){
            return lowestCommonAncestor(root -> right, p, q);
        }
        else{
            return root;
        }


        
    }
};

```