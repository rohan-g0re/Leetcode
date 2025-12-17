```cpp


class Solution {
public:
    bool hasCycle(ListNode *head) {

        while(head != nullptr){

            if (head -> val == INT_MAX) return true;
            
            else{
                head -> val = INT_MAX;
                head = head -> next; 
            }
        }
        return false;
    }
};

```