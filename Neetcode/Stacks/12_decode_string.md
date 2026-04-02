# BOTH HAD SAME PERFORMANCE ON LEETCODE

### Approach 1: heavy use of substring mechanisms

```cpp

class Solution {
public:
    string decodeString(string s) {
        int n = s.size();
        int open = 0, close = 0;

        while (close < n) {

            // 1. find first closing bracket
            bool found = false;
            for (int i = 0; i < n; i++) {
                if (s[i] == ']') { 
                    close = i;
                    found = true;
                    break;
                }
            }
            if (!found) break; // we have reached end such that the ending characters were letters and not brackets --> eg: 3[ab]cd



            // 2. find respective opening bracket --> by going in reverse
            for (int i = close; i >= 0; i--) {
                if (s[i] == '[') {
                    open = i;
                    break;
                }
            }


            // 3. get MULTI-DIGIT count by scanning left of open
            int num_end   = open - 1; // --> points at the units digit of the number 
            int num_start = num_end;

            while (num_start > 0 && isdigit(s[num_start - 1])) {
                num_start--;  // walk left collecting all digits
            }

            // get the final number from substring
            int count = stoi(s.substr(num_start, num_end - num_start + 1));




            // 4. build repeated string
            string to_repeat = s.substr(open + 1, close - open - 1);
            string replacement = "";
            for (int i = 0; i < count; i++)
                replacement += to_repeat;

            // 5. replace entire "123[...]" chunk with expansion
            //        start posi, number of elements  , replacement string
            s.replace(num_start, close - num_start + 1, replacement);

            // 6. update pointers

            // INTUITION --> we just need to update the close pointer to start of replacement string as THERE WILL NEVER BE A CLOSING BRACKET BEFORE the replaced string
            close = num_start;  // restart from where replacement was inserted
            n = s.size();
        }

        return s;
    }
};
```

### Approach 2: Using stack

```cpp

class Solution {
public:
    string decodeString(string s) {

        // 1. push into stack until you get closing bracket

        // 2. pop everything upto FIRST opening bracket and register the string 


        // 3. now go ahead for all the digits --> register the number

        // 4. calculate the string and push it in stack

        // 5. continue again 

        stack<string> st;

        for(auto& ch : s){

            if(ch == ']'){

                string temp_string = "";

                while(st.top() != "["){
                    temp_string.insert(0, st.top());
                    st.pop();
                }

                st.pop(); // pop the opening bracket

                int k = 0;
                int multiplier = 1;
                while(!st.empty() && isdigit(st.top()[0])){
                    k += stoi(st.top()) * multiplier;
                    st.pop();
                    multiplier *= 10;
                }

                // we have k and string --> now calculate the string and push it
                string replacement_string = "";
                for(int i = 0; i < k; i++){
                    replacement_string += temp_string;
                }

                st.push(replacement_string);

            }
            else{
                st.push(string(1, ch)); // converting characters to string if needed
            }
        }

        string result = "";
        while(!st.empty()){
            result.insert(0, st.top());
            st.pop();
        }

        return result;

    }
};

```