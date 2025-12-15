Given a binary tree, find the lowest common ancestor (LCA) of two given nodes in the tree.

According to the definition of LCA on Wikipedia: "The lowest common ancestor is defined between two nodes p and q as the lowest node in T that has both p and q as descendants (where we allow a node to be a descendant of itself)."

Example 1:

Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1
Output: 3
Explanation: The LCA of nodes 5 and 1 is 3.

Example 2:

Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4
Output: 5
Explanation: The LCA of nodes 5 and 4 is 5, since a node can be a descendant of itself according to the LCA definition.

****************

## Intuition

- LCA is the deepest node that has both p and q as descendants
- If we find p or q, return that node
- If both left and right subtrees return non-null, current node is LCA
- If only one subtree returns non-null, return that result

## BRUTE FORCE --> Find Paths and Compare

- Find path from root to p
- Find path from root to q
- Compare paths to find last common node

```
class Solution {
public:
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
        
        vector<TreeNode*> pathP, pathQ;
        findPath(root, p, pathP);
        findPath(root, q, pathQ);
        
        TreeNode* lca = nullptr;
        int i = 0;
        while (i < pathP.size() && i < pathQ.size() && pathP[i] == pathQ[i]) {
            lca = pathP[i];
            i++;
        }
        
        return lca;
    }
    
private:
    bool findPath(TreeNode* root, TreeNode* target, vector<TreeNode*>& path) {
        if (!root) return false;
        
        path.push_back(root);
        
        if (root == target) return true;
        
        if (findPath(root->left, target, path) || findPath(root->right, target, path)) {
            return true;
        }
        
        path.pop_back();
        return false;
    }
};
```

TC --> O(n) for finding paths
SC --> O(n) for storing paths

## OPTIMAL --> Recursive DFS

- Traverse tree recursively
- If current node is p or q, return it
- If both left and right return non-null, current is LCA
- Otherwise return the non-null result

```
class Solution {
public:
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q) {
        
        // Base case: if root is null or matches p or q
        if (!root || root == p || root == q) {
            return root;
        }
        
        // Search in left and right subtrees
        TreeNode* left = lowestCommonAncestor(root->left, p, q);
        TreeNode* right = lowestCommonAncestor(root->right, p, q);
        
        // If both left and right return non-null, root is LCA
        if (left && right) {
            return root;
        }
        
        // Otherwise return the non-null result
        return left ? left : right;
    }
};
```

## TC --> O(n) where n is number of nodes
## SC --> O(h) where h is height of tree (recursion stack)

