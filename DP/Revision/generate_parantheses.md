## INTUITIONS:

- only valid are counted
- always going to start with opening bracket and end with closing bracket

### BRUTE:

1. generate all
2. check each if valid?
3. return valid

## BETTER:

1. create valids only

# MAIN LOGIC

## 1. opening bracket can be added if available

## 2. Closing bracket can be added only if a parenthesis is op	en.

##### PROCESS --> Hence, we need to keep on passing the data of the open parentheses. First I tried to a flag, but when we return, setting a flag to false just means that all the parentheses are set,  BUT BUT BUT it is possible that we have 3 parentheses open and only one got closed. Hence, we are using a open_count To keep track of how many parentheses are currently open.

```cpp
class Solution {

private:
    void recurse(int opening, int closing, int open_count, string str, vector<string>& result){

        // 1. base case --> opening and closing zero --> push in result

        if(opening == 0 && closing == 0){
            result.push_back(str);
            return;
        }

        // 2. if opening available --> add that thing --> increment open_count
      
        if(opening > 0){
            recurse(opening - 1, closing, open_count + 1, str + '(', result);
        }

        // 3. if open_count > 0 && closing available --> add that thing --> decrement open_count

        if (open_count > 0 && closing > 0){
            recurse(opening, closing - 1, open_count - 1, str + ')', result);
        }
        return;
    }


public:
    vector<string> generateParenthesis(int n) {

        vector<string> result;

        recurse(n, n, 0, "", result);

        return result;

    }
};
```
