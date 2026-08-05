# ALGORITHM:
```bash

- 2 pointers - on each LL

- Whichever is less:
    - we store its next to continue
    - we update its next to the bigger number


```




```cpp
class Solution {
public:
    ListNode* mergeTwoLists(ListNode* list1, ListNode* list2) {

        // 1. Handle empty list cases first
        if (list1 == nullptr) return list2;
        if (list2 == nullptr) return list1;


        ListNode* dummy_node;
        
        ListNode* l1;
        ListNode* l2;

        // Set the first node for the sorted chain
        // ALSO setting both the pointers 
        
        if (list1 -> val <= list2->val){
            dummy_node = list1;
            l1 = list1 -> next;
            l2 = list2;
            
        }
        else{
            dummy_node = list2;
            l2 = list2 -> next;
            l1 = list1;
        }
        
        ListNode* temp = dummy_node;


        while (l1 != nullptr && l2 != nullptr){

            // if l1 smaller --> merge it

            if (l1 -> val <= l2 -> val){
                // update
                temp -> next = l1; 

                // inc
                l1 = l1-> next;
            }
            else{
                // update
                temp -> next = l2; 

                // inc
                l2 = l2 -> next;
            }

            temp = temp -> next;
        }

        // one of the lists might be remaning

        if (l1 != nullptr){
            temp -> next = l1;
        }
        else{
            temp -> next = l2;
        }

        return dummy_node;      
    }
};

```