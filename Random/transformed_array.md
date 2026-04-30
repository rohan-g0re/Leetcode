
# BRUTE --> WITHOUT using mod (%) for circular traversal

```cpp

class Solution {

public:
    vector<int> constructTransformedArray(vector<int>& nums) {

        int n = nums.size();

        vector<int> result;

        for (int i = 0; i < n; i++){

            // 1. +ve

            if (nums[i] > 0){
                
                int steps_to_be_taken = nums[i];
                int steps = 0;

                int j = i; 
                while (steps < steps_to_be_taken){
                    if (j == n-1) j = 0;
                    else j++;
                    steps++; 
                }

                // we got j at the right position now --> place this value in result array

                result.push_back(nums[j]);
                
            }

            
            // 2. -ve

            else if (nums[i] < 0){
                
                int steps_to_be_taken = abs ( nums[i] );
                int steps = 0;

                int j = i; 
                while (steps < steps_to_be_taken){
                    if (j == 0) j = n-1;
                    else j--;
                    steps++; 
                }

                // we got j at the right position now --> place this value in result array


                result.push_back(nums[j]);                
            }


            // 3. zero

            else{
                result.push_back(nums[i]);
            }


        }

        return result;
        
    }
};

```


# OPTIMAL 

```cpp

/*

INTUITION:
1. we have to add the nums[i] into i ---> so that we get the new position
2. we can modulo the addition we get to bring it in bounds

INTERESTING:

if nums[i] is positive then the following rule woud work --> 

    result[i] = nums[ ( i + nums[i] ) % n ]


BUTTTT this does not work when nums[i] is negative because the resulting index CAN BE NEGATIVE


Therfore to make a single rule ROBUST FOR NEGATIVE -->
    1. we add "n" into it -- so that we DEFINITELYL HAVE A positive number -- as { i + nums[i] ) % n } is less than n --> 

    2. the number recieved by adding n can be modded again incase the addition might be out of bounds

*/


class Solution {
public:
    vector<int> constructTransformedArray(vector<int>& nums) {

        int n = nums.size();

        vector <int> result (n);

        for(int i = 0; i < n; i++){
            result[i] = nums[ (((i + nums[i]) % n ) + n ) % n];
        }

        return result;
        
    }
};

```