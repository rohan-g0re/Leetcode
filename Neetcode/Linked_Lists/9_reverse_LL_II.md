## Semantics:

1. Left chain [0, left - 1]
2. Right Chain [right + 1, end]
3. Reverse Chain [left, right]
4. left_chain_dummy --> last node of left chain 
    - we need to link this to last reversed node
5. switch_chain_dummy --> first node to be reversed --> basically LL[left] 
    - we need to link this to first node of right chain after reversing
    - first node of right chain can be found at `mover` OR `front` after reversal is done




## Algorithm:

1. Phase 1: assign shit
    - if `left==1` then:
        - `left_chain_dummy == nullptr` bcoz there is no left chain to be linked later
        - `switch_dummy == head` bcoz its the first node to be reversed
    - else if left > 1:
        - traverse till the `left - 1` node
        - assign `left_chain_dummy` as that node
        - `switch_dummy = mover -> next` bcoz it will be the `left` node itself

2. Phase 2: Reversal
    - dont choose `prev` as left-1 --> does not help --> so choose nullptr --> ANY-WHICH-WAYS, we are going to link it later to the right chain.


3. Phase 3: Link Nodes
    1. linking reversed chain to right is easy
        - just link `switch_dummy` to right chain's first node, which is found at `mover` OR `front`

    2. linking left chain to last_node_to_be_reversed
        - left chain found at `left_chain_dummy`
        - last_node_to_be_reversed found at `prev`

#### IMPORTANT --> BUT if left == 1 then it means that left chain is empty --> which also means that the first node of LL WILL NOW BE the last node to be reversed, which was originally found at LL[right] --> currently at prev --> so return prev



```cpp

class Solution {
public:
    ListNode* reverseBetween(ListNode* head, int left, int right) {

        // 1. phase 1 reach left and assign shit

        ListNode* mover = head;
        ListNode* left_chain_dummy = nullptr;
        ListNode* switch_dummy = head;

        if(left != 1){

            for(int i = 1; i < left - 1; i++){
                mover = mover -> next;
            }
            left_chain_dummy = mover;
            switch_dummy = mover -> next;
        }


        // 2. reverse from left to right

        int total_nodes = right - left + 1;

        ListNode* prev = nullptr;
        mover = switch_dummy;

        while(total_nodes > 0){

            ListNode* front = mover -> next;
            mover -> next = prev;
            prev = mover;
            mover = front;

            total_nodes--;
        }

        // 3. relinking of chains & return
        switch_dummy -> next = mover; // link first reversed node with the right part of chain ---> right part being [right+1, end]


        if (left_chain_dummy != nullptr){ // because left can be 1 in which case we dont need to link dummy chain
            left_chain_dummy-> next = prev;
            return head;
        }


        // return prev if left chain empty
        return prev;

        
    }
};
```