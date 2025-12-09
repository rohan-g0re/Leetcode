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
            // handles the case where both are NOT null --> which means that both are on subtrees below

            // in such case we need the root itself bcoz this would SURELY BE THE FIRST TIME THIS HAS HAPPENED -->
            // which means this root is the actual answer

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

        // dont need to search the right subtree
        if (root -> val > max (p -> val, q -> val)){
            return lowestCommonAncestor(root -> left, p, q);
        }

        // dont need to search the left subtree
        else if (root -> val < min (p -> val, q -> val)){
            return lowestCommonAncestor(root -> right, p, q);
        }
        else{
            // becuause the value matched
            return root;
        }


        
    }
};

```