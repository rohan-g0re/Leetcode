## FAST AND SLOW POINTER
- move fast by 2 steps & slow by 1 step
- 2 cases:
    1. either they meet --> and we return true
    2. or the LL ends and the while-loop case terminates

```cpp
class Solution {
public:
    bool hasCycle(ListNode *head) {

        ListNode* fast = head;
        ListNode* slow = head;

        while(fast != nullptr && fast->next != nullptr){
            slow = slow -> next;
            fast = fast -> next -> next;

            if(slow == fast) return true;
        }

        return false;
        
    }
};
```