```cpp

class Solution {
public:
    vector<vector<int>> levelOrder(TreeNode* root) {

        if (!root) return{};



        queue <TreeNode*> q;

        vector <vector<int>> result;

        q.push(root);

        while (!q.empty()){

            int snapshot = q.size();
            
            vector <int> level;

            for (int i = 0; i < snapshot; i++){

                TreeNode* node = q.front();
                level.push_back(node->val);
                
                
                q.pop();
                if (node -> left != nullptr) q.push(node -> left);
                if (node -> right != nullptr) q.push(node -> right);

            }

            result.push_back(level);        

        }

        return result;
        
    }
};

```