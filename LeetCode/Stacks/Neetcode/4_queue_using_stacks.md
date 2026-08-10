## PUSH EXPENSIVE VERSION --> bcoz we do the complete pipeline of actions on every push action

```cpp

class MyQueue {

private:
    stack <int> s1; // actual queue functionalities 
    stack <int> s2; // helper stack

public:
    MyQueue() {
        
    }
    
    void push(int x) {

        // 1. empty s1 into s2 

        while (!s1.empty()) {
            s2.push(s1.top());
            s1.pop();
        }

        // 2. push x into s1

        s1.push(x);

        // 3. empty s2 into s1 again
        
        while (!s2.empty()) {
            s1.push(s2.top());
            s2.pop();
        }

    }
    
    int pop() {

        int top = s1.top();
        s1.pop();
        return top; 
    }
    
    int peek() {
        return s1.top();
    }
    
    bool empty() {
        return s1.empty();
    }
};

```


## POP EXPENSIVE VERSION --> bcoz we do the complete pipeline of actions on every pop action


```cpp

class MyQueue {

private:
    stack <int> s1; // actual queue functionalities 
    stack <int> s2; // helper stack

public:
    MyQueue() {
        
    }
    
    void push(int x) {
        s1.push(x);
    }
    
    int pop() {


        // 1. empty s1 into s2 

        while (!s1.empty()) {
            s2.push(s1.top());
            s1.pop();
        }

        // 2. pop and return the top element from s2

        int popped = s2.top();
        s2.pop();

        // 3. empty s2 into s1 again
        
        while (!s2.empty()) {
            s1.push(s2.top());
            s2.pop();
        }
        
        return popped; 
    }
    
    int peek() {
        
        
        // 1. empty s1 into s2 

        while (!s1.empty()) {
            s2.push(s1.top());
            s1.pop();
        }

        // 2. pop and return the top element from s2

        int topper = s2.top();

        // 3. empty s2 into s1 again
        
        while (!s2.empty()) {
            s1.push(s2.top());
            s2.pop();
        }
        
        return topper; 


    }
    
    bool empty() {
        return s1.empty();
    }
};

```