# LC 1004 - Medium


## INTUITION:
- keep 2 pointers
- EXPAND until the count of 0's reaches is valid
- SHRINK if the count of 0s is invalid
- as we have to return length - we can use the optimal version of the pattern 2


```cpp



class Solution {
public:
    int longestOnes(vector<int>& nums, int k) {

        int counter = 0;
        int l = 0;
        int r = 0;
        int n = nums.size();
        int maxlen = 0;

        while(r < n){

            if(nums[r] == 0)counter++;

            // SHRINK if invalid
            while(counter > k){
                // if 0 then decrement
                // or else keep moving the left pointer since we got 1
                if(nums[l] == 0) counter--;
                l++;
            }
            
            // EXPAND if valid
            // as the above while loop runs furst - hence we know that - if we are standing here - that means that the window is valid
            maxlen = max(maxlen, r - l + 1);
            r++;
        }
        return maxlen;
    }
};

```

## Post Solving Conclusions:
1. pattern 2 - optimal from striver does not mean that that we are supposed to use 'if' instead of 'while' 
2. IT MEANS THAT --> I am supposed to shrink the window to "JUST MAKE IT VALID"
    - the while loop over here basically deletes only one zero from end
    - but we need a while loop instead of an 'if' case to make that happen


# Complexities:
1. TC = O ( 2 * n)
    - in worst case --> my l and r pointers are going to travel the complete array

2. SC = O(1)