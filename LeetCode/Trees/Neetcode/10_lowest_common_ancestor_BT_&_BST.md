# BINARY TREE

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

# BINARY SEARCH TREE

## INTUITION:

- For BST we can explore based on the numbers

#### MAIN INTUITION --> Lca is Either the immediate parent or one of the numbers (p or q) --> hence based on the BST split logic, if we get such a node where p and q are on either sides of it --> IT IS THE LCA

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
            
            /*
            Handles 2 cases:
                1. Root matched to one of the P or Q nodes
                    --> which means the other one is the child
                    --> which means that this node is LCA
                
                2. Root -> val is in BETWEEN P and Q 
                    --> this means that p and q are no more on one side together
                    --> which means this p and q are in left and right subtree respectively
                    --> this can only happen if the current root is AN IMMEDIATE PARENT OF BOTH p and q
                    --> hence current node is the Least Common Ancestor
            */

            return root;
        }
      
    }
};
```