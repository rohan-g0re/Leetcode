# BRUTE:
1. push all elements from LL to vector
2. Get the nth node
3. search and destroy

--> BUT we cant do this since the numbers are **NOT UNIQUE** --> hence we might need to make a map or something to keep a track of homenay times is the number came already


# BETTER:
1. Find Length of LL
2. Find the node position on which we need to make the deletion
3. If:
    3.a. n == 1 --> delete head
    3.b. n > 1 --> you can perform simple deletion

**IMPORTANT --> while setting `mover -> next` we need to be sure that we are not addressing a null pointer's next - since it would give us a `NullPointerException`**

### Code:

```cpp
class Solution {
public:
    ListNode* removeNthFromEnd(ListNode* head, int n) {

        // 1. count length 

        int len = 0;
        ListNode* mover = head;

        while(mover != nullptr){
            len++;
            mover = mover -> next; 
        }

        // 2. count the target length to travel
        int target_node = len - n + 1;  // "+1" since without it -> deleting head is difficult in a aLInked List

        // 3. if n = 1 --> delete head

        mover = head;

        if (target_node == 1){
            head = head -> next;
            delete(mover);
            return head;
        }
        
        // 4. traverse till target and delete
        
        else{

            target_node--; // decrement bcoz our target node now is previous node of the node to be deleted

            while(target_node > 0){
                target_node--;
                if (target_node == 0){
                    
                    if (mover -> next -> next) mover -> next = mover -> next -> next;
                    else mover -> next = nullptr; // incase we are deleting tail then next should be direclty null OR ELSE we would have made an error by acccessing null's next pointer
                    return head;
                }
                mover = mover -> next;
            }

        }
        return head;
    }
};
```