# IMPORTANT CONCEPT --> 2 pointers in LL - something similar to Slow & Fast pointer but here, both of them have same speed

### `result_head` is basically a dummy node


## Brute - 1 

- Pass 1 add odds in result array
- Pass 2 add evens in result array

### But we are supposed to solve the problem in O(1) space complexity and O(n) time complexity. This approach is O(n) because we have two iterations over the linked list, but it uses O(n) space complexity because we are using an external array to store values

```cpp

class Solution {
public:
    ListNode* oddEvenList(ListNode* head) {

        if(head == nullptr)  return head;

        ListNode* mover = head;
        
        ListNode* result_mover = new ListNode(mover->val);
        ListNode* result_head = result_mover;

        mover = mover -> next;
        
        // 1. pass 1

        int counter = 2;

        while(mover){

            if(counter % 2 == 1){
                ListNode* temp = new ListNode(mover->val);

                result_mover -> next = temp;
                result_mover = result_mover -> next;

            }
            counter++;
            mover = mover -> next;
        }

        // pass 2

        counter = 2;
        mover = head -> next;

        // result pointers are fine
        
        while(mover){

            if(counter % 2 == 0){
                ListNode* temp = new ListNode(mover->val);

                result_mover -> next = temp;
                result_mover = result_mover -> next;

            }
            counter++;
            mover = mover -> next;
        }

        return result_head;
                
    }
};
```




## Optimal --> RELINK ALL THE NODES by using concept of 2 POINTER nodes --> 1. odd pointer && 2. even pointer && 3. change links for each

#### INTUITION
- --> if both pointers jump (even number of nodes) then --> EVEN pointer will always be ahead
- --> if LL has odd number of nodes then EVEN pointer will be behind


```cpp
class Solution {
public:
    ListNode* oddEvenList(ListNode* head) {

        if(head == nullptr)  return head;

        ListNode* odd = head;
        ListNode* even = head -> next;
        ListNode* even_head = head -> next;



        while(even != nullptr && even -> next != nullptr){
            odd -> next = odd -> next -> next;
            even -> next = even -> next -> next;

            // it is the next location because we changed the links now
            odd = odd -> next;
            even = even -> next;
        }

        // link both the chains
        odd -> next = even_head;

        return head;        
    }
};
```