## MASSIVE BIG BRAIN --> just OVERWRITE current node's values WITH next node's values --> this is an inplace delete because the original values does not exist anymore

```cpp
class Solution {
public:
    void deleteNode(ListNode* node) {

        node = node->next val = node->next->val;
        node->next = node->next->next;
        
    }
};
```