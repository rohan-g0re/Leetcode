# Valid Palindrome - I

### INTUITIONS:

1. Compare a string with the reverse of itself.
2. Use 2 pointers to start from each end and keep comparing UNTIL found difference or cross
3. we dont need to REMOVE punctuations --> **we can simply IGNORE punctuations** --> **isalnum()**

### ADDITIONAL FUNCTIONS:

1. remove punctuations
2. convert to lowercase --> **tolower()**

### Code:

```cpp

class Solution {
public:
    bool isPalindrome(string s) {

        int l = 0;
        int r = s.size() - 1;

        while (l <= r){

            // ignore punctuations on left side 

            if (!isalnum(s[l])){
                l++;
                continue;
            }

            // ignore punctuations on right side 
        
            if (!isalnum(s[r])){
                r--;
                continue;
            }

            // compare the actual characters 
        
            if (tolower(s[l]) != tolower(s[r])){
                return false;
            }
            l++;
            r--;
        }
        return true;
    
    }
};

```

# Valid Palindrome - II

### INTUITIONS:

#### 1. AT MOST ONE DELETION --> so it can be ZERO deletion as well (valid palindrome itself)

#### 2. when found first mismatch --> we can skip either of the elements and the rest of the string should be valid --> if not then it means we encountered ANOTHER mismatch (hence mismatch > 1)

### Code:

```cpp

class Solution {

private:
bool is_valid(string& s, int l, int r){
    while(l <= r){
        if (s[l] != s[r]) return false; // bcoz we found second mismatch
        l++;
        r--;
    }
    return true;
}

public:
    bool validPalindrome(string s) {

        int l = 0;
        int r = s.size() - 1;

        while (l <= r){
            // we know that we only have english smallcase letters --> hence no need for code to ignore symbols and capital letters

            if (s[l] == s[r]){
                l++;
                r--;
                continue;
            }

            // first mismtach --> go recurse on string in 2 ways
                // 1. either by skipping left character
                // 2. and by skipping righ character
                // - it will be VALID in AT LEAST ONE WAY
                // - if its not --> it means that we found ANOTHER MISMATCH --> hence it fails the "at most one" case.

            else{
                // 1st mismatch --> so atleast one of them should return true...
                return is_valid (s, l+1, r) || is_valid (s, l, r-1);
            }
          
        }

        return true; //since we have valid palindrome ansd hence we need to make zero deletions.

    }
};

```
