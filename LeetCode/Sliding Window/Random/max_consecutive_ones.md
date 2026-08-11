# LC 1004 - Medium

# BETTER - Shrink Left pointer to make the window valid

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
1. pattern 2 - Better
2. This is better becuase in shrinking the window from left side "MY MAX_LEN was not preseerved" --> hence i will need to take extra efforts to bring my window to max_len size and then MORE efforts to find the new max_len 


# Complexities:
1. TC = O ( 2 * n)
    - in worst case --> my l and r pointers are going to travel the complete array

2. SC = O(1)



# OPTIMAL - Preserving window size to current maxlen

## INTUITION:
- keep on incrementing r
- if window is valid - update the max len
- if invalid - increment the left pointer && dont increment the maxlen --> what will happen is:
    - if the element that was just removed from the window was ZERO --> then at next iteration 



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


            // if valid --> increment maxlen
            if(counter <= k){
                maxlen = max(maxlen, r - l + 1);
            }

            // in invalid --> shrink from left
            else{
                if(nums[l] == 0) counter--;
                l++;
            }

            r++; // will do this anywhich-way
        }
        return maxlen;
    }
};

```

# Complexities:
1. TC = O (n)
2. SC = O(1)