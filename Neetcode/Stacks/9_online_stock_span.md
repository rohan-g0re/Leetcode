# INTUITION: MONOTONIC STACK WITH SQUASHING ELEMENTS

### With a simple monotonic stack setup --> TLE

```cpp

class StockSpanner {

private:
    stack<int> price_stack;

public:
    StockSpanner() {    }
    
    int next(int price) {
        price_stack.push(price);

        stack<int> temp;

        int span = 0;

        // 1. count span and by popping into temp stack
        while(!price_stack.empty() && price_stack.top() <= price){
            span++;
            temp.push(price_stack.top());
            price_stack.pop();
        }

        // 2. fill up price stack again

        while(!temp.empty()){
            price_stack.push(temp.top());
            temp.pop();
        }

        return span;
        
    }
};


```



### With a monotonic stack setup with **"SQUASHING THE ELEMENTS"** --> no need of repushing & revisiting the elements again as we *"store the SPAN"* --> bring TC from O(n^2) to O(n)

```cpp

class StockSpanner {

private:
    stack<pair<int, int>> price_stack;

public:
    StockSpanner() {
        
    }
    
    int next(int price) {
        
        int span = 1;
        
        // base case - empty stack
        if (price_stack.empty() || price_stack.top() > price) {
            price_stack.push({price, 1});
        }
        else{
            while(!price_stack.empty() && price_stack.top().first <= price){
                span += price_stack.top().second;
                price_stack.pop();
            }

            // pushing the element after calculating the span
            price_stack.push({price, span});

        }
        return span;
    }
};

```