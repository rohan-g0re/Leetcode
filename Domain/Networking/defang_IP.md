# LC 1108 - Easy


## 2 ways:
- sub string replace
- construct new array


## Substring Replace

```cpp
class Solution {
public:
    string defangIPaddr(string address) {

        int i = 0;

        while(i < address.size()){
            // 1. get the dot
            // 2. replace the dot
            // 3. move the i

            if(address[i] == '.'){
                address.replace(i, 1, "[.]");
                i += 2;
            }
            else{
                i++;
            }
        }

        return address;
        
    }
};
```


## New Array 

```cpp

class Solution {
public:
    string defangIPaddr(string address) {

        string result = "";

        for(char c : address){
            if(c == '.'){
                result += "[.]";
            }
            else{
                result += c;
            }

        }

        return result;
    }
};
```