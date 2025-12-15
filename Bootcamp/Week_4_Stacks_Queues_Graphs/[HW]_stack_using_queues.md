Implement a last-in-first-out (LIFO) stack using only two queues. The implemented stack should support all the functions of a normal stack (push, top, pop, and empty).

Implement the MyStack class:

- void push(int x) Pushes element x to the top of the stack.
- int pop() Removes the element on the top of the stack and returns it.
- int top() Returns the element on the top of the stack.
- boolean empty() Returns true if the stack is empty, false otherwise.

Notes:

- You must use only standard operations of a queue, which means only push to back, peek/pop from front, size, and is empty operations are valid.
- Depending on your language, the queue may not be supported natively. You may simulate a queue using a list or deque (double-ended queue) as long as you use only a queue's standard operations.

Example 1:

Input
["MyStack", "push", "push", "top", "pop", "empty"]
[[], [1], [2], [], [], []]
Output
[null, null, null, 2, 2, false]

Explanation
MyStack myStack = new MyStack();
myStack.push(1);
myStack.push(2);
myStack.top(); // return 2
myStack.pop(); // return 2
myStack.empty(); // return False

****************

## Intuition

- Stack is LIFO (Last In First Out)
- Queue is FIFO (First In First Out)
- To simulate stack with queues, we need to reverse the order
- Strategy: Use one queue as main storage, transfer elements to get last element

## APPROACH 1 --> Using Two Queues

- q1: main queue
- q2: helper queue
- For push: add to q1
- For pop/top: transfer all but last element from q1 to q2, get last element, swap queues

```
class MyStack {
private:
    queue<int> q1;
    queue<int> q2;
    
public:
    MyStack() {
        
    }
    
    void push(int x) {
        q1.push(x);
    }
    
    int pop() {
        // Transfer all but last element to q2
        while (q1.size() > 1) {
            q2.push(q1.front());
            q1.pop();
        }
        
        // Get the last element
        int top = q1.front();
        q1.pop();
        
        // Swap queues
        swap(q1, q2);
        
        return top;
    }
    
    int top() {
        // Transfer all but last element to q2
        while (q1.size() > 1) {
            q2.push(q1.front());
            q1.pop();
        }
        
        // Get the last element
        int top = q1.front();
        q2.push(q1.front());
        q1.pop();
        
        // Swap queues
        swap(q1, q2);
        
        return top;
    }
    
    bool empty() {
        return q1.empty();
    }
};
```

## APPROACH 2 --> Using Single Queue

- For push: add element, then rotate queue to make it last
- For pop/top: front element is the top

```
class MyStack {
private:
    queue<int> q;
    
public:
    MyStack() {
        
    }
    
    void push(int x) {
        q.push(x);
        
        // Rotate queue: move all elements before x to the back
        int size = q.size();
        for (int i = 0; i < size - 1; i++) {
            q.push(q.front());
            q.pop();
        }
    }
    
    int pop() {
        int top = q.front();
        q.pop();
        return top;
    }
    
    int top() {
        return q.front();
    }
    
    bool empty() {
        return q.empty();
    }
};
```

## TC --> 
- push: O(n) - need to rotate queue
- pop: O(1)
- top: O(1)
- empty: O(1)

## SC --> O(n) for storing elements

