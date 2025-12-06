

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
    vector<int> postorderTraversal(TreeNode* root) {
        
        stack <TreeNode*> st;

        TreeNode* current = root;
        TreeNode* lastvisited  = nullptr;

        vector <int> result;

        // main driver 

        while (!st.empty() || current != nullptr){

            // recursively go traverse left until you ARE A NULL NODE

            while ( current != nullptr ){
                st.push(current);
                current = current -> left;
            }

            // help me!!! - somebody from stack --> SO YOU PEEK

            TreeNode* peek = st.top();


            // NOW 2 cases:
            
            // 2.1 if the peeked node has right child && it has not been visited yet --> traverse right node 

            if (peek -> right != nullptr && peek -> right != lastvisited){
                current = peek -> right;
            }

            // 2.2 it does not have a right child or else it was PROCESSED earlier --> then it means you dont have anything left --> HENCE, PRINT & PROCESS IT;

            else{
                result.push_back(peek -> val);
                lastvisited = st.top(); // (can also be <peek> itself) we are doing this bcoz once printed - we dont want the parent to come agin this path 


// THIS ALSO GETS CHECKED IN CASE 2.1 -- where we are checking if the right node that you are talking about is not the one already done - or else it would be an infinite loop (process right child - comebackup - "OOHH we still have a right child" :DUMB:)                

                st.pop();
            }
        }

        return result;

    }
};


```