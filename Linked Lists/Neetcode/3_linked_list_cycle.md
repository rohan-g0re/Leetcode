GO on altering all the values in the linked list with `INT_MAX` --> if you find an `INT_MAX` then thats the loop

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
