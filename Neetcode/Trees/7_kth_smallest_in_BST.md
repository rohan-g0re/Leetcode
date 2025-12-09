# TRICK!!!!!


# INORDER TRAVERSAL OF BST RETURNS SORTED ORDER

```cpp

/**
 * Definition for a binary tree node.
 * struct TreeNode {
 *     int val;
 *     TreeNode *left;
 *     TreeNode *right;
 *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
 *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
 *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
 * };
 */
class Solution {
public:
    int kthSmallest(TreeNode* root, int k) {

        stack<TreeNode*> st;

        TreeNode* current = root;

        int counter = 0;

        while (current != nullptr || !st.empty()){

            // STEP 1: traverse in depth in left

            while (current != nullptr){
                st.push(current);
                current = current -> left;
            }

            // STEP 2.1: now we are on null --> PEEK and get the top node from stack

            TreeNode* peek = st.top();
            st.pop();

            // STEP 2.2: register this peeked node
            
            counter++;
            if (counter == k) return peek -> val;

            // STEP 3: we move to right 
            current = peek -> right;
        }
        return -1;
      
    }
};

```