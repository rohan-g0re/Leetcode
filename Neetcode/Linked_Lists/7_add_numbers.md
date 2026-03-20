# IMPORTANT TRICK -->  Any time if you want to create a new linked list, use the dummy node concept DUMMY NODE CONCEPT 
#### 1. We basically creates 2 nodes: one as the head of new LL (which will not move) and the other which moves on the new LL
#### 2. this resembles to the general strategy that we use for LLs
#### 3. Also the first type of new node (which does not move) can be of 2 types: it can be at position 0 which means we will be returning `dummy_node`      ---*OR OR OR*---      it can be at posi -1 which means we will be returning `dummy_node->next`





# BRUTE 
- we can add traverse l1 and l2 to get the numbers
- add them
- create a new LL based on the sum


# BETTER

## INTUITION: as the digits are already in reverse order --> it means they are already in order units-tens-hundred.. --> which means they are already in the order in which we add two numbers

### Algo:
1. traverse simultaneously
    - add nodes and carry
    - calculate units digit of sum which will be added --> using sum % 10
    - calculate carry for later --> using sum / 10
2. COMPLETE until both reach nullptr
3. if there is any carry left add that as a new node


**We are creating dummy_node at position -1 --> Hence, we will be returning `dummy_node->next`**


### Code:

```cpp
class Solution {
public:
    ListNode* addTwoNumbers(ListNode* l1, ListNode* l2) {

        ListNode* dummy_node = new ListNode(-1); // we are going to its NEXT later
        ListNode* mover = dummy_node; // we are going to its NEXT later
        int carry = 0;

        while(l1 != nullptr || l2 != nullptr){ // both of them should finish for the loop to end

            // 1. calculate sum only for list nodes that exist
            int sum = 0;
            if(l1) sum += l1 -> val;
            if(l2) sum += l2 -> val;
            sum += carry; 

            // 2. create new node for a digit --> add it to the new LL --> shift mover ahead
            ListNode* temp = new ListNode(sum%10);
            mover -> next = temp;
            mover = mover -> next;

            // 3. calculate carry for next round
            carry = sum / 10;

            // 4. update l1 and l2 if not already on null pointer
            if (l1) l1 = l1 -> next; // we dont want to shift it if it is already on a nullptr
            if (l2) l2 = l2 -> next; // we dont want to shift it if it is already on a nullptr

        }

        // 5. Add carry as a NODE if it exists after all the addition.
        if (carry > 0){
            ListNode* temp = new ListNode(carry);
            mover -> next = temp;
            mover = mover -> next;
        }

        // 6. return dummynode's next bcoz that should be the actual head of LL
        return dummy_node -> next;     
    }
};
```