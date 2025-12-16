## Remember, there is no point of the constructor as of now because ANYTHING AND EVERYTHING that you define in the constructor is disappeared after the construction execution is done.


```cpp

class MyStack {

private:
    queue <int> q;

public:
    MyStack() {
    }
    
    void push(int x) {

        int snapshot = q.size();

        q.push(x);

        for (int i = 0; i < snapshot; i++){
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