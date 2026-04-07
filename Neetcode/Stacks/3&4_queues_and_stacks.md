
#  Implement Queue using Stacks.

```cpp

class MyQueue {

private:
    stack<int> S1;
    stack<int> S2;

public:
    MyQueue() {
        
    }
    
    void push(int x) {

        // s1 is the main stack

        // 1. pop everything into S2

        while(!S1.empty()){
            S2.push(S1.top());
            S1.pop();
        }

        // 2. push the new number

        S1.push(x);

        // 3. pop everthing from s2 back to s1
        
        while(!S2.empty()){
            S1.push(S2.top());
            S2.pop();
        }
    }
    
    int pop() {

        int temp = S1.top();
        S1.pop();
        return temp;
    }
    
    int peek() {

        return S1.top();
        
    }
    
    bool empty() {

        return S1.empty();
        
    }
};

```


# Implement Stack using Queues

```cpp

class MyStack {
private:
    queue <int> q;

public:
    MyStack() {  }
    
    void push(int x) {
        // 1. push the new element in queue
        q.push(x);

        // 2. pop all remaining elements and insert it back in queue
        for(int i = 0; i < q.size() - 1; i++){
            q.push(q.front());
            q.pop();
        }
    }
    
    int pop() {
        int temp = q.front();
        q.pop();
        return temp;
    }
    
    int top() {
        return q.front();        
    }
    
    bool empty() {
        return q.empty();
    }
};

```