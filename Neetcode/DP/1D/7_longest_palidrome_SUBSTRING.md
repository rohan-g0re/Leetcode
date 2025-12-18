## Approach 1: Recursion --> TLE 

##### IMPORTANT --> LOGIC --> if current substring is valid then return it --> else we will go further and explore by removing elements from either ends

```cpp

class Solution {
public:

    bool valid_palindrome(string s, int l, int r){
        
        while(l <= r){
            if (s[l] != s[r]){
                return false;
            }
            l++;
            r--;
        }
        return true;
    }

    string helper(string& s, int i, int j){

        // base cases

        // 1.1 invalid substring
        if (i > j) return "";

        // 1.2 single length string - is always valid palindrome
        if (i == j) return string (1, s[i]);



        // 2. logic 

        // if current substring is valid then return it --> else we will go further and explore by removing elements from either ends

        if (valid_palindrome(s, i, j)){
            
            return (s.substr(i, j-i + 1));

        }

        // 3. as the current substr is not valid we recurse by removing elements from left and right side - at a time 

        string left = helper (s, i+1, j);
        string right = helper (s, i, j-1);


        // 4. return logic

        if (left.size() > right.size()){
            return left;
        }
        return right;

    }

    string longestPalindrome(string s) {

        string curr_string = "";
        return helper(s, 0, s.size() - 1);

        
    }
};

```



## IT NEEDS 2D DP to solve it in memoization - so skip


## Approach 2: two pointer

#### LOGIC --> INSTEAD of validating palindrome from outside --> start validating them from center --> so for a string "bab" you set your pointers l and r at 'a' and then start moving outwards to find "WHAT IS THE BIGGEST SUBSTRING THAT 'a' IS A PART OF" 


## IMPORTANT: we want the l and r to start their lookup from the center of the PALINDROMIC STRING --> and, we are not talking about the center of the given string  

```cpp

class Solution {
public:

    string longestPalindrome(string s) {

        int global_max = 0;
        string result = "";

        int n = s.size();

        // IMNPORTANT --> the for loop is helpful such that it lets us TEST every element as the CENTER OF THE PALINDROMIC STRING

        for (int i = 0; i < n; i++){
            

            // IF the chosen S[i] IS THE CENTER OF "ODD-LENGTH" PALINDROME - then l and r can be initilaized as a single element

            int l = i;
            int r = i;
            
            while(l >= 0 && r < n && s[l] == s[r]){
                // the while statement makes sure that the current string is palindrome 
                
                if (r - l + 1 > global_max){
                    result = s.substr(l, r-l+1);
                    global_max = r-l+1;
                }

                l--;
                r++;
            }

            // IF S[i] IS THE CENTER OF "EVEN-LENGTH" PALINDROME - then l and r CANNOT be initilaized as a same element --> and hence we need to have two different elements as the center

            l = i;
            r = i+1;
            
            while(l >= 0 && r < n && s[l] == s[r]){
                // the while statement makes sure that the current string is palindrome 
                
                if (r - l + 1 > global_max){
                    result = s.substr(l,r-l+1);
                    global_max = r-l+1;
                }

                l--;
                r++;
            }

        }

        return result;
        
    }
};

```