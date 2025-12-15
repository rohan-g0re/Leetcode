Given the root of a binary tree, imagine yourself standing on the right side of it, return the values of the nodes you can see ordered from top to bottom.

Example 1:

Input: root = [1,2,3,null,5,null,4]
Output: [1,3,4]

Example 2:

Input: root = [1,null,3]
Output: [1,3]

Example 3:

Input: root = []
Output: []

****************

## Intuition

- Right side view means the rightmost node at each level
- Can use BFS (level-order traversal) and take last node of each level
- Or use DFS with right-first traversal, tracking depth

## BRUTE FORCE --> BFS Level Order Traversal

- Do level-order traversal
- For each level, take the last node (rightmost)

```
class Solution {
public:
    vector<int> rightSideView(TreeNode* root) {
        
        vector<int> result;
        if (!root) return result;
        
        queue<TreeNode*> q;
        q.push(root);
        
        while (!q.empty()) {
            int levelSize = q.size();
            TreeNode* rightmost = nullptr;
            
            for (int i = 0; i < levelSize; i++) {
                TreeNode* node = q.front();
                q.pop();
                
                rightmost = node;  // Last node in level is rightmost
                
                if (node->left) q.push(node->left);
                if (node->right) q.push(node->right);
            }
            
            result.push_back(rightmost->val);
        }
        
        return result;
    }
};
```

TC --> O(n) where n is number of nodes
SC --> O(n) for queue

## OPTIMAL --> DFS Right-First Traversal

- Traverse right subtree first, then left
- Track depth, add first node seen at each depth

```
class Solution {
public:
    vector<int> rightSideView(TreeNode* root) {
        
        vector<int> result;
        dfs(root, 0, result);
        return result;
    }
    
private:
    void dfs(TreeNode* root, int depth, vector<int>& result) {
        if (!root) return;
        
        // If this is the first node at this depth, add it
        if (depth == result.size()) {
            result.push_back(root->val);
        }
        
        // Traverse right first, then left
        dfs(root->right, depth + 1, result);
        dfs(root->left, depth + 1, result);
    }
};
```

## TC --> O(n) where n is number of nodes
## SC --> O(h) where h is height of tree (recursion stack)

