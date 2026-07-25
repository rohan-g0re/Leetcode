## Intuition:

1. every node should have get the "MAX-SO-FAR"
2. If the current node is good --> increment count and change max

##### UPGRADE --> we can also do this using a global count variable - passed by reference --> so we dont create local copies anywhere

```cpp


class Solution {

private:

    int dfs(TreeNode* node, int curr_max){

        // base case
        if(node == nullptr) return 0;

        //logic
        // good node when val is more than max

        int count = 0;

        if(curr_max <= node -> val){
            count++;
            curr_max = node -> val;
        }

        // explore
        count += dfs(node -> left, curr_max);
        count += dfs(node -> right, curr_max);

        return count;

    }

public:
    int goodNodes(TreeNode* root) {

        return dfs(root, INT_MIN);
      
    }
};
```
