# SIMPLE SOLUTION


```cpp

class Solution {
public:
    bool isTrionic(vector<int>& nums) {

        int n = nums.size();
        int i = 0;

        while (i + 1 < n && nums[i] < nums[i+1]){
            i++;
        }


        // check if i moved from "zero" --OR-- reached the end already --> false
        int p = 0;
        if (i == 0 || i >= n - 1) return false;
        else{
            p = i;
        }

        while (i + 1 < n && nums[i] > nums[i+1]){
            i++;
        }

        // check if i moved from "p" --OR-- reached the end already --> false
        if (i == p || i >= n - 1) return false;

        // no need to store q for comparison 


        while (i + 1 < n && nums[i] < nums[i+1]){
            i++;
        }

        // check if i has reached the end --> this direclty checks if it moved from the last checkpoint 
        // and the last check-point was when we compared i with p 
        // 


        if (i == n - 1) return true;

        return false;

        
        
    }
};

```


# THIS FOLLOWING THING NEVER WORKED BTW --> OVER ENGINEERED TO THE BRIM!!

/*


## INTUITION:

- need to figure out the times when it is NOT trionic  
    - failing the pattern

--> we have to write code such that any other case fails the pattern


## BRUTE: 

```cpp
// need to make sure that p and q are different --> can keep a last valuable index


*/



class Solution {
public:
    bool isTrionic(vector<int>& nums) {

        int n = nums.size();

        // we need all 4 sets present, therefore cant be less than 4 --- right?
        if (n < 4) return false;


        int last_valuable = INT_MAX;
        int shift = 0;

        for (int i = 0; i < n; i++){

            // 1. increasing check

            if (shift < 1 && i+1 < n &&  nums[i+1] > nums[i]){
                last_valuable = i;
                continue;
            }

            // 2. the first shift
            else if(shift <= 1 && i+1 < n && nums[i + 1] <= nums[i]){

                // making sure that "0" and "P" are different
                if (i > last_valuable && shift == 0) shift++;
                // since the p is 0 itself
                else return false;

                last_valuable = i;

                // since we need strictly decreasing and hence it cant be equal
                if (nums[i+1] == nums[i]) return false; 

                continue;
            }
            
            
            // 3. the second shift
            else if(shift >= 1 && i+1 < n && nums[i + 1] > nums[i]){

                shift = 2;
                last_valuable = i;
                if ( i + 1 == n - 1) break;
                continue;
            }

            else break;

        }


        if (shift == 2 && last_valuable == n-2) return true;

        return false;



        
    }
};

```



