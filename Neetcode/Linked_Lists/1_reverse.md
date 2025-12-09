```cpp
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     ListNode *next;
 *     ListNode() : val(0), next(nullptr) {}
 *     ListNode(int x) : val(x), next(nullptr) {}
 *     ListNode(int x, ListNode *next) : val(x), next(next) {}
 * };
 */

class Solution {
public:
    ListNode* reverseList(ListNode* head) {

        stack<int> st;
        ListNode* temp = head;


        // STEP 1: PUSH ALL VALUES IN STACK

        while(temp != nullptr){
            st.push(temp->val);
            temp = temp -> next;
        }

        // STEP 2: Start from head AGAIN and reassign values from stack
        
        temp = head;
        while(!st.empty()){
            temp -> val = st.top();
            st.pop();
            temp = temp -> next;
        }

        return head;


    }
};
```