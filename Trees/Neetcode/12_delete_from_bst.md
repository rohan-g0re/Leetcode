# Initial Attempt --> could not solve one case --> if the succesor has right subtree then what to do

### MAIN IDEA --> find the smallest successor in tree --> delete it by replacing it with its right subtree

- Why this works:

  1. we know that successor wont have a left child
  2. BUT it can have a right subtree - which we dont traverse (since its not needed for finding successor)
  3. hence we just assign the right subtree --> even if it is null - we are okay with it
- **ALSO this can be done in left subtree by finding Biggest Predecessor**

# **IMPORTANT NOTE --> as we need to delete the node in end --> all functions must PASS TreeNodes BY REFERENCE**

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
private:

    int successor(TreeNode*& root){

        if(root -> left != nullptr) {
            return successor(root -> left);
        }

        // gottcha here --> found the successor
      
        // 1. store value 
        int succ = root -> val;

        /*
        2. delete node: BY SETTING IT AS RIGHT SUBTREE
            --> LOGIC
            - set set as null node
        */
        root = root -> right;
      

        // 3. return value
        return succ;

    }

    void dfs(TreeNode*& node, int key){

        // 1. base cases
        if(node == nullptr) return;


        // 2 --> if match
        if(node -> val == key){

            // 2.1 if right exists --> replace with smallest successor
          
            if(node -> right != nullptr){
                // find succ && delete succ && return succ value
                int succ = successor(node -> right);
                node -> val = succ;
            }

            // 2.2 if right does not exist --> just link directly to left node
            else{
                if(node -> left == nullptr){
                    node = nullptr;
                    return;
                }
                else{
                    node = node -> left; // should handle null nodes as well
                }
            }

            return;
        }



        // 3. if not --> then explore wrt BST properties
        else{
            if(node -> val > key){
                dfs(node -> left, key);
            }
            else{
                dfs(node -> right, key);
            }
        }


        return;
    }


public:
    TreeNode* deleteNode(TreeNode* root, int key) {

        if(root == nullptr) return root;

        dfs(root, key);

        return root;
      
    }
};
```