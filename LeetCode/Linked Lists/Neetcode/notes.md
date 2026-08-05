# Basics:

- array has fixed sixed && are stored in continuous locations --> CANNOT increase or decrease size
- LL is in NON-CONTINUOUS location in memory
- TRaversal:
  - node format: data, pointer to next node
    - starting point of LL is called **HEAD of LL**
    - last node has a next of `nullptr`--> called as the **TAIL of LL**
- Uses:
  - data structures: stack and queue
  - applications: web browser --> but its a **Doubly Linked List**

# struct definition

```cpp

struct Node{
    int data;
    Node* next;
    // we are pointing to the memory address of the next node hence the * mark 
    // the datatype of that node is going to be "Node" itself, which we are declaring here


    // as of now we have cmade 2 empty boxes basically
    // 1. empty box which will store data
    // 2. empty box which will get the pointer to next node

    // HENCE NOW WE NEED TO FILL THIS NODE BASED ON THE LL --> HENCE WE NEED A CONSTRUCUTOR


    Node(int data1){        // constructor with only data
        data = data1;
        next = nullptr;
    }
    Node(int data1, Node* next1){       // constructor with data && next node
        data = data1;
        next = next1;
    }

}

```

- struct does not have OOPs features like encapsulation, inheritance, and polymorphism.

# difference between Node and Node* declaration

## Part 1:

- if i declare as:
  ```cpp
  Node x = Node(2, nullptr);
  cout << x;
  ```
- What this does:
  - it has created x has an object
  - it will give ERROR at cout as we cant print an object
  - so to print values from an object we use `.abcd()`
  - so i can do:
    ```cpp
    cout<<x.data;       // prints the data which is 2
    cout<<x.next;       // prints the next node's memory address which is currenlty null
    ```

## Part 2:

- if i declare as:
  ```cpp
  Node x* = new Node(2, nullptr);
  cout << x;
  ```
- What this does:
  - FIRST OF ALL WE NEED TO USE THE `new` keyword --> **RETURNS THE MEMORY LOCATION of new object created**
  - it has created an object which has the data and next node's pointer - **and the pointer to that object is stored in x**
  - so now it will NOT give ERROR at cout as we CAN print the memory address
  - so to print values stored at a memory address we need to use `->` syntax as x is like an iterator now
  - so i can do:
    ```cpp
    cout<<x->data;       // prints the data which is 2
    cout<<x->next;       // prints the next node's memory address which is currenlty null
    ```

# Basic Codes:

## IMPORTANT --> Never TAMPER THE HEAD of LL


### 1. Converting array to LL

#### Algorithm

```cpp
# Algorithm to Convert Array to Linked List

1. Set `head` as a new node with the first element of the array.
2. Set `mover` pointer to `head` for traversal.
3. For each remaining element in the array (from index 1 to n-1):
    a. Create a new node `temp` with current array value.
    b. Set 'mover's next pointer to `temp`.
    c. Move `mover` to `temp` (advance the pointer).
4. Return the `head` (start of the linked list).
```

#### Code

```cpp
class Solution {
  public:
    Node* arrayToList(vector<int>& arr) {
        Node* head = new Node(arr[0]);
        Node* mover = head;
        int n = arr.size();

        for(int i = 1; i < n; i++){
            Node* temp = new Node(arr[i]);
            mover->next = temp;
            mover = mover->next;
        }
        return head;
    }
};
```


### 2. Length of given LL

#### Algorithm

```cpp
# Algorithm to find Length of LL

1. traverse while the temp node is VALID
2. Maintain a counter like `len`

```

#### Code

```cpp
class Solution{
  public: 
    int lengthOfLL(Node* head){
      int len = 0;
      Node* temp = head;

      while(temp){
        len++;
        temp = temp -> next;
      }

      return len;
    }
};
```

### 3. Search an element in LL

#### Algorithm

```cpp
# Algorithm to find Length of LL

1. traverse while the temp node is VALID
2. Check everytime if `temp->data == key`

```

#### Code

```cpp
class Solution{
  public: 
    bool searchLL(Node* head, int key){
      Node* temp = head;

      while(temp){
        if (temp->data == key) return true;
        temp = temp -> next;
      }

      return false;
    }
};
```


# Deletion Codes:

### 1. Deletion of head of LL

#### Algorithm

```cpp

1. initialize temp to head
2. increment head to head -> next
3. free / delete temp
4. return temp
```
#### Code


```cpp
class Solution{
  public: 
    Node* del1(Node* head){

      // Base Case --> If head itself does not exist
      if (head == nullptr) return head;

      // ---
      Node* temp = head;
      head = head -> next;
      
      delete(temp);

      return head;
    }
};
```



### 2. Deletion of tail of LL

#### Algorithm

```cpp

1. initialize temp to head
2. increment temp until you reach  `temp -> next == nullptr`
3. free / delete temp
4. return head
```
#### Code


```cpp
class Solution{
  public: 
    Node* del2(Node* head){

      // Base Case --> If head itself does not exist
      if (head == nullptr) return head;

      // ---
      // 1 2 3 4 n
      
      Node* temp = head;
      while (temp -> next != nullptr){
        temp = temp -> next;
      }
      
      delete(temp);

      return head;
    }
};
```



### 3. Deletion of kth element in LL


- Cases:
  - k == 1 --> delete head
  - k == out of bounds
  - k == middle node
  - k == tail

##### INTUITION: maintain `prev` and `temp` --> if `temp` reaches kth node then --> set `prev-> next == prev -> next -> next` --> and delete(temp)
- this same logic works for k == tail because in that case, previous's next will become a nullptr, which is true for temp --> so no need to write different code block for that case

#### Algorithm

```cpp

1. maintain prev, temp, counter(based on position of temp) --> increment temp and prev in tandem
2. if counter == k:
  - 2.1 change next of prev 
  - 2.2 delete temp
3. return temp
```


#### Code


```cpp
class Solution{
  public: 
    Node* del3(Node* head, int k){

      // Base Case 1 --> If head itself does not exist
      if (head == nullptr) return head;

      // Case 1: k == 1
      if (k == 1){
        Node* temp = head;
        head = head -> next;
        delete (temp);
        return head;
      }

      // Case 2, 3, 4:
      int counter = 0;
      Node* prev = nullptr;
      Node* temp = head;

      while (temp){
        counter++;

        if (counter == k){
          // link prev correctly
          prev -> next = prev->next->next;

          // delete temp
          delete (temp);

          break;
        }

        prev = temp;
        temp = temp->next;
      }
      return head;
    }
};
```


### 4. Deletion from LL based on value

- just remove based on target_value


#### Code

```cpp
class Solution{
  public: 
    Node* del4(Node* head, int target_value){

      // Base Case 1 --> If head itself does not exist
      if (head == nullptr) return head;

      // Case 1: target at head
      if (head->data == target_value){
        Node* temp = head;
        head = head -> next;
        delete (temp);
        return head;
      }

      // Case 2, 3, 4: target value somewhere else
      
      Node* prev = nullptr;
      Node* temp = head;

      while (temp){
        if (temp->data == target_value){
          // link prev correctly
          prev -> next = prev->next->next;
          // delete temp
          delete (temp);
          break;
        }
        prev = temp;
        temp = temp->next;
      }
      return head;
    }
};
```

# Insertion Codes:

### 1. Insertion at Head

#### Algorithm

```cpp
1. create a node temp
2. set temp->next = head
3. return temp
```

#### Code:
```cpp
class Solution {
public:
    Node* insertAtHead(Node* head, int value){
        Node* temp = new Node(value); // next will be null
        temp -> next = head;
        return temp;
    }
};
```

---

### 2. Insertion at Tail

#### Algorithm

```cpp
2. traverse till last element
1. create temp
3. point last element's next to next
```

#### Code:
```cpp
class Solution {
public:
    Node* insertAtTail(Node* head, int value);

    // base case --> no head

    if (head == nullptr){
        return new Node*(value);
    }

    // 1 2 3 4 n
    Node* mover = head;
    while(mover -> next != nullptr){
        mover = mover -> next;
    }
    Node* temp = new Node(value);
    mover -> next = temp;
    
    return head;
};
```

---

### 3. Insertion at Kth Position

#### Algorithm

```cpp
- k can be between 1 to n+1
- handle case for head == nullptr
- handle case for k == 1


1. traverse till k-1
2. create temp with: data = target && next = mover->next
3. change mover's next to temp

```

#### Code:
```cpp
class Solution {
public:
    Node* insertAtKth(Node* head, int k, int value){
        
        if (head == nullptr){
            // insert of k == 1 else dont do anything
            if (k == 1)return new Node(value);
            else return head;
        }

        if (k == 1){
            return new Node(value, head);
        }

        // -----
        int counter = 0;
        Node* mover = head;

        while(mover){
            counter++;

            if (counter == k-1){

                // create a node with data && next
                Node* temp = new Node(value, mover->next); // or we could do $temp->next = mover->next$ to connect

                mover->next = temp;
                break;
            }
            mover= mover->next;
        }

        return head;
    }
};
```

---

### 4. Insertion before Value X

#### Algorithm

```cpp
// 1 2 3 4 n
// insert 5 before 4

- target value at head --> create and insert before head
- target value somewhere else:
    - if traverse till mover->next == target_value:
        create new node and insert in between of mover && mover->next

```

#### Code:
```cpp
class Solution {
public:
    Node* insertBeforeValue(Node* head, int target_value, int x){
        
        if (head == nullptr)return head;

        if ( head->data == target_value){
            return new Node(x, head);
        }

        // -----
        Node* mover = head;

        while(mover){
            
            if (mover->next->data == target_value){

                // create a node with data && next
                Node* temp = new Node(x, mover->next); // or we could do $temp->next = mover->next$ to connect

                mover->next = temp;
                break;
            }
            mover= mover->next;
        }
        return head;
    }
};
```