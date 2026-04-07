### Implemented NGE for Daily Temperatures problem.



```cpp

class Solution {
public:
    vector<int> dailyTemperatures(vector<int>& temperatures) {
        
        stack <int> stack;

        int n = temperatures.size();

        vector <int> ngeResult(n, 0); 
        
        for (int i = n-1; i >= 0; i--){

            if (stack.empty()){
                ngeResult.push_back(0);
                stack.push(temperatures[i]);
            }
            else if (temperatures[i] < stack.top()){
                // valid NGE
                ngeResult[i] = stack.top();
                stack.push(temperatures[i]);
                
            }
            // stack .top is not NGE --> find the NGE by popping
            else{

                while (!stack.empty()){
                    if (stack.top() > temperatures[i]){
                        break;
                    }
                    stack.pop();
                }

                // we have either found out NGE at top or stack is empty

                if (stack.empty()){
                    // no NGE
                    ngeResult[i] = 0;
                    stack.push(temperatures[i]);
                }
                else{
                    ngeResult[i] = stack.top();
                    stack.push(temperatures[i]);
                }

            }

        }

        return ngeResult;


    }
};



```