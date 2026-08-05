```cpp

class Solution {
public:
    int evalRPN(vector<string>& tokens) {

        stack<int> stack;


        for (string s : tokens){
            if (s == "+" ||s == "-" || s == "*" || s == "/"){
                
                // the naming is to represent the order in the arithmetic --> "a" should be before "b" in equations
                
                int b = stack.top();
                stack.pop();
                int a = stack.top();
                stack.pop();


                if (s == "+"){
                    int res = a + b;
                    stack.push(res);
                }
                else if (s == "-"){
                    int res = a - b;
                    stack.push(res);
                }
                else if (s == "*"){
                    int res = a * b;
                    stack.push(res);
                }
                else if (s == "/"){
                    int res = a / b;
                    stack.push(res);
                }

            }
            else{
                stack.push(stoi(s));
            }
        }

        return stack.top();
        
    }
};

```