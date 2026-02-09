## INTUITIONS:
1. We DONT NEED to preserve the locations of numbers --> BUT WE DIFINITELY need to know all the numbers apart from it --> "order does not matter, content does"

2. Cant use DIVISION which is a big disadvantage --> or else we could have gone with dividing the total sum

## Approach 1 --> Using prefix and suffix 
1. Calculate prefix and suffix arrays
2. fill first and last position of array --OR-- find how to multiply numbers directly by 1 (since their respective multiple is out of bounds)
3. rest of the numbers can be filled diagonally --> which means for ith position in result = multiply i-1 from prefix and i+1 from suffix

```cpp
class Solution {
public:
    vector<int> productExceptSelf(vector<int>& nums){

        int n = nums.size();
        vector <int> prefix (n, 1);
        vector <int> suffix (n, 1);
        vector <int> result (n, 1);

        // 1. calculate prefix

        int prod = 1;
        for (int i = 0; i < n; i++){
            prod *= nums[i];
            prefix[i] = prod;
        }

        // 2. calculate suffix

        prod = 1;
        for (int i = n-1; i >=0; i--){
            prod *= nums[i];
            suffix[i] = prod;
        }

        // 3. Fill result arrray 

        result[0] = suffix[1];
        result[n-1] = prefix[n-2];

        for (int i = 1; i < n-1; i++){
            result[i] = prefix[i-1] * suffix[i+1];
        }

        return result;

    }
};
```


#### we can also do this by not using different arrays for prefix and suffix -AND- directly do everythign in the result array itself