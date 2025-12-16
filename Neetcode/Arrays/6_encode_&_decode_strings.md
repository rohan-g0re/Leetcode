## INTUITIONS: 
1. Each word can only be at max of 200 length
2. There can be at max 100 words

## Atempt 1:
- we can choose some sign as a delinmiter -- such as $
- but there can be strings which have $ in them 
    - for them we need to first travrse ALL THE WORDS AND edit the strings by adding a "\" before them 
        --> this is something like latex --> this would hel us tell that next character is not benig used as a delimiter 



## SOLUTION --> ADD numbering before words so that we now how many upcoming characters are the real word



```
hello --> 005hello

    problems:
        - 003 005
        - 008 005hello
```

## solution for this problem --> we add a delimiter after our number 

```
    008# 005hello --> the # tells us that we are supposed to count next 8 words as string
```


```cpp
class Solution {
public:

    string encode(vector<string>& strs) {

        /*
        
        1. Get length 
        2. Convert to string with lenght + "#"
        3. append this "custom_delimiter" to the actual string
        4. return the new string

        */

        string encoded_string = "";

        for (auto& str : strs){
            int size = str.size();
            encoded_string += to_string(size) + "#" + str;
        }

        return encoded_string;
    }


    vector<string> decode(string s) {

        /*
        hello wo#rld --> 5#hello6#world

        1. 2 pointer loop (i guess) for counting from 0 to #
        2. Capture those numbers and convert to int --> this is curr_length
        3. start from next element from # and run for curr_length
            --> keep appending those many characters to a string
            --> when loop ends - append it to result vector
        
        */
         vector<string> result;
        int i = 0;
        
        while (i < s.size()) {
            // Step 1: Find the delimiter '#'
            int delimiter_pos = s.find('#', i);
            
            // Step 2: Extract the length
            int length = stoi(s.substr(i, delimiter_pos - i));
            
            // Step 3: Extract the string (starts after '#')
            int start = delimiter_pos + 1;
            string decoded_str = s.substr(start, length);
            
            result.push_back(decoded_str);
            
            
            // Step 4: VERY IMPORTANT Move to next encoded string
            i = start + length;


            
        }
        
        return result;
        

    }
};
```