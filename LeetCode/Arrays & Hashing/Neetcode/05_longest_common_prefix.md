
```cpp

/*

flow
flower
flower

So ever if we find a lesser length of common substing OR EVEN A LONGER SUBSTRING --> we are supposed to update the lenght of the string && the string itself

NEXT 

Carry the commonthing around --> which means:
1. CONSIDER the common_prefix as first word
2. Carry common_prefix to second word and make changes in common_prefix if needed
3. Continue


*/


class Solution {
public:
    string longestCommonPrefix(vector<string>& strs) {

        string common_prefix = strs[0];

        for (auto& str : strs){

            if(common_prefix.size() == 0) return "";

            int pointer = 0;

            while(pointer < min (common_prefix.size(), str.size()) ){

                if (common_prefix[pointer] != str[pointer]){
                    common_prefix = common_prefix.substr(0, pointer);
                    break;
                }
                pointer++;
            }

            // it can be possible that no mismatch was found and hence did not update the common_prefix --> such as flower and flow --> the loop exits when the length ends and not when there was a mismatch --> hence the update condition was not executed --> therefore we need to add the updatting line again as given below

            common_prefix = common_prefix.substr(0, pointer);
        }

        return common_prefix;
        
    }
};

```

# Python Code

## Approach 1: Carry the result prefix

1. set a string as result
2. compare it letter by letter with each string
3. if mismatch --> set the successful/slice as result string

- run the inner loop for at max smallest length
- we update the bool if result is changed --> if result did not change this means that "string s was prefix of result" in which case we still need to shrink the result
- if prefix we need to set only the relevant length as result

```python
class Solution:
    def longestCommonPrefix(self, strs: List[str]) -> str:
        
        result = strs[0]

        for s in strs:

            change = False

            for i in range (min(len(s), len(result))):
                if(s[i] != result[i]):
                    result = s[:i]
                    change = True
                    break
            
            if(change == False): result = s[:min(len(s), len(result))]

        return result
```
