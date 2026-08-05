# LC 146 - Medium

- doubly linked list --> becasue deleting becomes very easy
- insert at tail --> since it is the LATEST end of the LL
- delete from head -> next --> since it is the OLDEST end of LL (head/tail are DUMMIES)
- Keep a map for the node



```cpp
struct Node{

    int key;
    int value;
    Node* prev;
    Node* next;

    // constructor to create this type of objects
    Node(int k, int v){
        key = k;
        value = v;
        prev = nullptr;
        next = nullptr;
    }

};


class LRUCache {
private:
    int cap;
    unordered_map<int, Node*> mp;
    Node* head;   // dummy --> oldest side
    Node* tail;   // dummy --> latest side

    // fully detach a node from wherever it currently sits
    void remove(Node* node){
        node -> prev -> next = node -> next;
        node -> next -> prev = node -> prev;
    }

    // insert just BEFORE tail --> this is now the LATEST
    void insert_at_tail(Node* node){

        // 1. links at back
        tail -> prev -> next = node;
        node -> prev = tail -> prev;
        // 2. links in front
        tail -> prev = node;
        node -> next = tail;
    }

public:
    LRUCache(int capacity) {

        cap = capacity;
        head = new Node(0, 0);
        tail = new Node(0, 0);

        // linking also 
        head -> next = tail;
        tail -> prev = head;
    }
  
    int get(int key) {

        // 1. get from map

        if(mp.find(key) != mp.end()){
            
            Node* temp = mp[key];

            // delete from current place + move to tail (mark as latest)
            remove(temp);
            insert_at_tail(temp);

            return temp -> value;
        }

        return -1;
    }
  
    void put(int key, int value) {

        // CASE 1 --> key already exists --> update value + move to tail
        if(mp.find(key) != mp.end()){

            Node* temp = mp[key];
            temp -> value = value;   // MUST update value

            remove(temp);
            insert_at_tail(temp);

        }

        // CASE 2 --> new key
        else{

            // if full --> evict OLDEST (head -> next), NOT the dummy head itself
            if((int)mp.size() == cap){

                Node* lru = head -> next;

                mp.erase(lru -> key);   // erase THIS node's key from map
                remove(lru);
                delete lru;
            }

            // TASK 1 --> insert at tail - as this is the latest --> and undertsand that we basically insert BETWEEN last actual node AND TAIL 
            Node* temp = new Node(key, value);
            insert_at_tail(temp);

            // TASK 2 --> also add this in map
            mp[key] = temp;
        }
    }
};

```