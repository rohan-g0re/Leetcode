#### While checking with closed bracked make sure that we take into account that the stack can be empty
#### Also the stack can have elements left after loop (more precisely, opening brackets) - if thats the case then it is again false


```cpp

class Solution {
public:
    bool isValid(string s) {


        stack<char> stack;

        unordered_map <char, char> map;
        map[')'] = '(';
        map['}'] = '{';
        map[']'] = '[';

        for (char bracket : s){
            if ( bracket == '(' || bracket == '{' || bracket == '['){
                stack.push(bracket);
            }
            else{
                if ( stack.empty() || map[bracket] != stack.top()) return false;
                stack.pop();

            }
        }

        if (stack.size() == 0) return true;

        return false;
        
    }
};

```