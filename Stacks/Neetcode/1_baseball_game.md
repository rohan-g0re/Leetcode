##### The else condition can easily handle the logic for the rest of the numbers. We don't need to explicitly give it `1 || 2 || 3...` etc

```cpp

class Solution {
public:
    int calPoints(vector<string>& operations) {

        stack<int> st;
        for (auto& ele : operations ){
            
            // 1. if C then pop
            if (ele == "C"){
                st.pop();
            }
            // 2. if D then top * 2 and push 

            else if(ele == "D"){
                st.push(st.top() * 2);
            } 
            // 3. if + then pop two and add and push

            else if(ele == "+"){
                int sum = st.top();
                int temp = sum;
                st.pop();
                sum += st.top();
                
                st.push(temp);
                st.push(sum);

            } 
            // 4. if num then push

            else{
                st.push(stoi(ele));
            }
        }

        int result = 0;

        while(!st.empty()){
            result += st.top();
            st.pop();
        }

        return result;
      
    }
};

```