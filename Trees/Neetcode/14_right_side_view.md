
## INTUITION:
1. We have to explore right side first
2. A node on ANY LEFT SUBTREE is seen ONLY IF --> ALL THE PREVIOUS RIGHT SUBTREES WERE SMALLER
3. hence we need to maintain the current height that we are exploring && the maximum height that we have already explored




```cpp

class Solution {

private:
    void dfs(TreeNode* root, vector<int>& result, int curr_height, int& max_height){

        curr_height += 1; // increment height as this is a new node

        if(curr_height > max_height){
            result.push_back(root -> val); // this depth is first time seen as any node here is to be added to result
            max_height = curr_height;       // this is the new max depth
        }

        // explore --> right first

        if(root -> right != nullptr) dfs(root -> right, result, curr_height, max_height);
        if(root -> left != nullptr) dfs(root -> left, result, curr_height, max_height);
        
        return;
    }

public:
    vector<int> rightSideView(TreeNode* root) {

        if(root == nullptr) return {};

        vector<int> result;
        int maxi = 0;

        dfs(root, result, 0, maxi);

        return result;
    }
};
```