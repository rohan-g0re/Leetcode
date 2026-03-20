# USING MAP OF POINTERS

#### 2 pass 

#### pass 1 --> make nodes
#### pass 2 --> link nodes


## Map structure


```cpp

    // key             value
<old_node_pointer, new_node_pointer>

```

## CODE:

```cpp

class Solution {
public:
    Node* copyRandomList(Node* head) {

        Node* mover = head;
        unordered_map<Node*, Node*> mp;

        // PASS 1

        while(mover != nullptr){
            // 1. create a node 

            Node* temp = new Node (mover->val);

            // 2. make a map entry

            mp[mover] = temp;

            // 3. shift mover ahead
            mover = mover -> next;
        }


        // PASS 2

        mover = head;

        while(mover != nullptr){

            Node* copy = mp[mover];
            copy -> next = mp[mover -> next];
            copy -> random = mp[mover -> random];

            mover = mover -> next;

        }
        return mp[head];
    }
};

```