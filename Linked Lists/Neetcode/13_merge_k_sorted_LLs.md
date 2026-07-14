

## INTUITION -> pick the smallest from heap as it will be the next one to merge

##### Therefore heap will be containing --> < value , LL head itself >

- val bcoz it will be responsible for heapify()
- LL head to traverse the LL when we pop off the node

```cpp
/*

1. create heap <int, Node*>
2. while heap is not empty and heap.top != nullptr
    
    2.1 GET val --> pick val from heap and append to answer

    2.2 GET Node --> jump to next 
        --> if next is nullptr then dont push
    
    2.3 Push next in heap 
        
*/


class Solution {
public:
    ListNode* mergeKLists(vector<ListNode*>& lists) {

        // 1. create heap
        priority_queue <pair<int, ListNode*>, 
        vector <pair<int, ListNode*>>, 
        greater <pair<int, ListNode*>>
        > min_heap;

        
        // initial fill with vals & heads of all the LLs 

        for(auto& ele : lists){
            if(ele != nullptr){
                min_heap.push({ele -> val, ele});   
            }
        }


        // 2. while every pointer is null

        ListNode* dummy = new ListNode();
        ListNode* mover = dummy;
         


        while(!min_heap.empty()){

            int current_val = min_heap.top().first;
            ListNode* Node = min_heap.top().second;
            min_heap.pop();


            // create - append - move in answer - move in LL

            ListNode* temp = new ListNode(current_val);
            mover -> next = temp;
            mover = mover -> next;
            Node = Node -> next;


            if(Node != nullptr){
                min_heap.push({Node -> val, Node});
            }
        }

        return dummy-> next;
    }
};

```