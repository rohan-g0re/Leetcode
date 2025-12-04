

## NAIVE APPROACH --> Use a pair datatype which stores the min value till now in the stack



```cpp
class MinStack {
private:

    stack <pair<int, int>> st;
        
public:
    MinStack() {

        
    }
    
    void push(int val) {

        // if empty then push minimum directly

        if (st.empty()) st.push({val, val});

        // else push the value by comparing with top

        else{
            int curr_min = st.top().second;
            if (val > curr_min) st.push({val, curr_min});
            else st.push({val, val});
        }

        
    }
    
    void pop() {

        st.pop();
        
    }
    
    int top() {

        return st.top().first;
        
    }
    
    int getMin() {

        return st.top().second;
        
    }
};

```

###### SC == O( 2 * n) --> which is expensive



## Approach 2: Mathematical way to keep miniimum variable O(1) intact -- even storing history

##### 2 * val - prev_min = new_val

###### needed to add long long to avpid integer overflow

```cpp
class MinStack {
private:
    stack<long long> st;  // ✓ Use long long
    long long minimum;     // ✓ Use long long

public:
    MinStack() {
        minimum = LLONG_MAX;
    }
    
    void push(int val) {
        if (st.empty()) {
            st.push(val);
            minimum = val;
        } else {
            if (val >= minimum) {
                st.push(val);
            } else {
                // Save old minimum before updating
                long long oldMin = minimum;
                minimum = val;
                
                // Encode using long long arithmetic
                long long encoded = 2LL * val - oldMin;
                st.push(encoded);
            }
        }
    }
    
    void pop() {
        if (st.empty()) return;
        
        long long topVal = st.top();
        st.pop();
        
        if (topVal < minimum) {
            // Decode previous minimum
            minimum = 2LL * minimum - topVal;
        }
    }
    
    int top() {
        if (st.empty()) return -1;  // or handle error
        
        long long topVal = st.top();
        if (topVal < minimum) {
            return (int)minimum;
        }
        return (int)topVal;
    }
    
    int getMin() {
        return (int)minimum;
    }
};


```