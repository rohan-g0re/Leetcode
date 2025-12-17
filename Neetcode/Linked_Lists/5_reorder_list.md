## NAIVE APPROACH:
```bash 

1. TOOLS: queue and stack
2. keep pushing all the elements in both the data stuctures
3. for the final order:
    - we need one from queue (because it represents the actual order)
            &&&&&
    - one from stack (because it represents the reverse order)

```


```cpp
class Solution {
public:
    void reorderList(ListNode* head) {
        
        ListNode* temp = head;
        queue <int> q;
        stack <int> st;


        while (temp != nullptr){
            q.push (temp -> val);
            st.push (temp -> val);
            temp = temp -> next;
        }
        

        temp = head;
        int node_number = 1;

        while(temp != nullptr){

            if (node_number % 2 != 0){ //odd node gets left side value
                temp -> val = q.front();
                q.pop();
            }
            else{
                temp -> val = st.top();
                st.pop();
            }
            node_number++;
            temp = temp -> next;
        }
    }
};

```


### ISSUE: WE ARE ACTUALLY WASTING SPACE BY STORING EACH VALUE TWICE

## WE CAN SOLVE THIS BY KEEPINGSTORING VALUES IN A VECTOR and then using 2 pointers to update --> we would still need a node_number

#### BETTER CODE: 

```cpp

class Solution {
public:
    void reorderList(ListNode* head) {
        
        ListNode* temp = head;
        vector <int> copy_ll;
        
        while (temp != nullptr){
            copy_ll.push_back(temp -> val);
            temp = temp -> next;
        }
        

        temp = head;
        int node_number = 1;

        int l = 0;
        int r = copy_ll.size() - 1;
        

        while(temp != nullptr){

            if (node_number % 2 != 0){ //odd node gets left side value
                temp -> val = copy_ll[l];
                l++;
            }
            else{
                temp -> val = copy_ll[r];
                r--;
            }
            node_number++;
            temp = temp -> next;
        }
    }
};

```