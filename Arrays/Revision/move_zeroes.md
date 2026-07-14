## INTUITIONS:

1. THE MAIN CHALLENGE is do do in inplace

## OPTIMAL SOLUTION --> 2 Pointer approach

```
1. have r pointer looking for non-zero numbers
2. l should always have a zero
3. swap when r is found --> increment both 
4. END WHEN r reaches n
```

## CODE

```cpp
class Solution {
public:
    void moveZeroes(vector<int>& nums) {

        int n = nums.size();
        int l = -1;


// STEP 1 --> Find the first zero --> and initlaize l to it --> initialize r to l+1 

        for (int i = 0 ; i < n; i++){
            if (nums[i] == 0){
                l = i;
                break;
            }
        }

        if (l == -1) return;

        int  r = l + 1;

/*
STEP 2 --> here we start the swapping logic --> WE EXPLORE ONLY USING r --> l is a lagging pointer 

    - if non-zero <r> found --> swap l and r --> increment l and r 
    - if zero found by <r> --> increment r
    - continue till <r> reaches end 
*/

        while (r < n){

            if (nums[r] != 0){
                swap(nums[l], nums[r]);
                l++;
                r++;
            }
            else if(nums[r] == 0){
                r++;
                continue;
            }
 
        }

        return;
        
    }
};
```