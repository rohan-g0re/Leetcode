```cpp
struct Node{

    int key;
    int value;
    Node* prev;
    Node* next;

    // constructor to create theis type of objects
    Node(int k, int v){
        key = k;
        value = v;
        prev = nullptr;
        next = nullptr;
    }

}


class LRUCache {
private:
    int cap;
    unordered_map<int, Node*>;
    Node* head;
    Node* tail;

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
      
    }
  
    void put(int key, int value) {

      
    }
};

/**
 * Your LRUCache object will be instantiated and called as such:
 * LRUCache* obj = new LRUCache(capacity);
 * int param_1 = obj->get(key);
 * obj->put(key,value);
 */
```
