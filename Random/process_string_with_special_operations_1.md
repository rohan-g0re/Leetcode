## Intuition:
    - Basic string operations
    - earlier thought of using stack
        - BUT emptying it was expensive
        - also Reversing the popped string was an added complexity 



```cpp

class Solution {
public:
    string processStr(string s) {
        int n = s.size();

        string result = "";

        for(int i = 0; i < n; i++){

            if(isalnum(s[i])){
                result.push_back(s[i]);
            }

            else if (s[i] == '*'){
                if(result.size() > 0) result.pop_back();
            }

            else if(s[i] == '#'){
                result += result;
            }

            else{
                reverse(result.begin(), result.end());
            }

        }

        return result;
       
    }
};

```