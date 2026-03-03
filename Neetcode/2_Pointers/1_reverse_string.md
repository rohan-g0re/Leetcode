```cpp
class Solution {
public:

    void my_function (vector<char>& s, int l, int r){

        if (l >= r){
            return;
        }

        swap (s[l], s[r]);
        my_function(s, ++l, --r);

    }


    void reverseString(vector<char>& s) {

        int l = 0;
        int r = s.size()-1;


        my_function(s, l, r);
        
    }
};
```