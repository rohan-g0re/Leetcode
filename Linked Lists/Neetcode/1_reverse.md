## Approach 1: Push elements in stack and rewrite the list


```cpp

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

##### But we are using O(n) space for stack which is not great --> hence we need to bring it down to O(1)


## Approach 2: change the directions of links --> basically use temp pointers to move forward and change links

```cpp


class Solution {
public:
    ListNode* reverseList(ListNode* head) {

        ListNode* mover = head;
        ListNode head = new ListNode();

        while(mover != nullptr){

            // 1. store front which is basically the next node in original Linked List

            ListNode* front = mover -> next;

            // 2. change direction of link for the current node in reverse direction

            mover -> next = prev;

            // 3. update prev by incrementing it to mover

            prev = mover;

            // 4. update mover to front

            mover = front;

        }

        return prev; // bcoz mover will be on nullptr after upgrading - which is the reason why we came out of the loop --> hence the head of this LL will be on prev (the only valid node we have)
    
    }
};
```