## INTUITIONS:

1. Compare a string with the reverse of itself.
2. Use 2 pointers to start from each end and keep comparing UNTIL found difference or cross

## ADDITIONAL FUNCTIONS:

1. remove punctuations
2. convert to lowercase --> **tolower()**

## INTUITION:

1. we dont need to REMOVE punctuations --> we can simply IGNORE punctuations --> **isalnum()**

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

                returnfalse;

            }

            l++;

            r--;

        }

        returntrue;

    

    }

};


```
