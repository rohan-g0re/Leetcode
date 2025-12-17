
```cpp

class Solution {
public:
    ListNode* removeElements(ListNode* head, int val) {

        // SANITY CHECK 1: we might have empty list
        if(head == nullptr) return nullptr;
        
        
        // STEP 1. what if the initial elements are the target itself

        while (head!= nullptr && head -> val == val){
            head = head -> next;
        }

        // SANITY CHECK 2: we might have deleted the complete list
        if(head == nullptr) return nullptr;

        
        
        
        // STEP 2. delete from middle or tail

        ListNode* temp = head;

        while(temp != nullptr && temp-> next != nullptr){
            // basically we can only stop when both are true so it means that we would stop after we have reached out of bounds


            // 2.1 if match - connect with the skip node

            if (temp -> next -> val == val){
                temp -> next = temp -> next -> next;

                // no need to move the temp because we have already changed the next node for temp, therefore the WHILE CHECK would still make sense

            }
            else{
                // as there was NO MATCH --> we explicitly need to move temp 
                temp = temp -> next;
            }
        }

        return head;
    }
};

```