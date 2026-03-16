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

    Node(int data1, Node* next1){
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

### 1. Converting array to LL


```cpp



```