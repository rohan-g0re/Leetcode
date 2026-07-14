#### While checking with closed brackets make sure that we take into account that the stack can be empty

#### IMPORTANT CONDITION --> also the stack can have elements left after loop (more precisely, opening brackets) - if thats the case then it is again false


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
                if ( stack.empty() || map[bracket] != stack.top()) return false; // directly comparing if we there is mismatch of parantheses --OR-- the count of some brackets is more which leads to mismatch

                // if it is a match - then pop
                stack.pop();

            }
        }

        if (stack.size() == 0) return true;

        return false;
        
    }
};

```