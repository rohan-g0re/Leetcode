# USE Monotonic Stack Logic for NGE (Next Greatest Element) --> BUT PUSH INDEXES because if you just push temperatures, the returned count would npt be correct even ig you count pops

### Verbose edition

```cpp

class Solution {
public:
    vector<int> dailyTemperatures(vector<int>& temperatures) {
        
        stack<int> st;   // store INDEX, not temperature

        int n = temperatures.size();
        vector<int> ngeResult(n, 0); 
        
        for (int i = n-1; i >= 0; i--) {

            if (st.empty()) {
                ngeResult[i] = 0;
                st.push(i);            // push index
            }

            else {
                // pop until we find a hotter day
                while (!st.empty() && temperatures[st.top()] <= temperatures[i]) {
                    st.pop();
                }

                if (st.empty()) {
                    ngeResult[i] = 0;
                } else {
                    ngeResult[i] = st.top() - i;
                }

                st.push(i);
            }
        }

        return ngeResult;
    }
};

```


### TC --> O ( 2 N )