# Iterative Postorder Traversal (Single Stack Approach)

## Intuition

Postorder traversal: **Left → Right → Root**. Challenge: we encounter parents before children, but must process children first.

## Key Insight

1. **Go left as deep as possible** (push nodes onto stack)
2. **When stuck (current = null)**, peek at stack top
3. **Two cases**:
   - Right subtree exists and not visited → process right subtree first
   - No right child OR right already processed → process current node

## Algorithm

**Data Structures**: Stack (unprocessed nodes), `current` (exploration pointer), `lastvisited` (prevents infinite loops)

**Steps**:
1. Go left deep: while `current != null`, push and move left
2. Peek stack top when `current == null`
3. **Case 1**: `peek->right != null && peek->right != lastvisited` → set `current = peek->right`
4. **Case 2**: Otherwise → add to result, set `lastvisited = peek`, pop stack

**Why `lastvisited`?** After processing right subtree, we return to parent. Without tracking, we'd re-process the right child infinitely.

## Complexity

- **Time**: O(n) - each node visited once
- **Space**: O(h) - stack height (worst case O(n) for skewed tree)

---

```cpp

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
                lastvisited = st.top(); // (can also be <peek> itself) we are doing this bcoz once printed - we dont want the parent to come again this path 


// THIS ALSO GETS CHECKED IN CASE 2.1 -- where we are checking if the right node that you are talking about is not the one already done - or else it would be an infinite loop (process right child - comebackup - "OOHH we still have a right child" :DUMB:)                

                st.pop();
            }
        }

        return result;

    }
};


```