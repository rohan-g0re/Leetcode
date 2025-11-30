

## Approach 1: Recursion --> TLE

```cpp
class Solution {
public:

    bool valid_palindrome(string& s){
        int l = 0;
        int r = s.size() -1;
        while(l <= r){
            if (s[l] != s[r]){
                return false;
            }
            l++;
            r--;
        }
        return true;
    }

    int helper(string& s, string& curr_str, int curr_index){

        // base case
        if (curr_index == s.size()){
            if (valid_palindrome(curr_str)){
                return curr_str.size();
            }
            else{
                return 0;
            }
        };


        // logic 


        //  "PICK" the current element
        curr_str.push_back(s[curr_index]);
        int left = helper (s, curr_str, curr_index + 1);

        //  "DONT PICK" the current element
        curr_str.pop_back();        
        int right = helper (s, curr_str, curr_index + 1);


        // return logic 
        return max(left, right);

    }


    int longestPalindromeSubseq(string s) {
        string curr_string = "";
        return helper(s, curr_string, 0);        
    }
};

```


## Approach 2: Needs 2D dp - so skip