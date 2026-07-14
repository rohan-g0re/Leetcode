
# INTUITION -->  for each number we need to find its 2x at both the sides --> if that is valid then increment triplet count

## Brute Force: n2


## BETTER with 2 maps --> the global freq map of numbers (which is computed before) && a current map which shows freq of numbers that have passed

#### Finding values from map
we can find if the 2*nums[i] is present in both tables 

- number of "TWICES" in left --> prev[2*nums[i]] 
- number of "TWICES" in right --> next[ 2 * prev[nums[i]  ]]


#### Calculating Contribution
- but there can be multiple ways a set can be formed --> here comes combinatorics --> 
- EACH "TWICE" in left can be picked in only 1 way --> similarly for "TWICE" in right --> therefore the answer is left twices into right twices
- this will give us all the counts of set that the given nums[i] is included.


## ISSUES WITH LARGE numbers
- need to use long long
- need to use 0LL in max since max needs both numbers in same dtpype
- need to use MOD since multiplication of large number also overflows `long long`
- during returning we need to MOD again to make it valid
- during returning adding `int` typecasting



# Code:

```cpp


class Solution {
public:
    int specialTriplets(vector<int>& nums) {

        const long long MOD = 1e9  + 7;

        unordered_map<int, long long> global_freq;
        unordered_map<int, long long> prev_freq;

        int n = nums.size();
        // 1. global frequency map filling
        for(int i = 0; i < n; i++){
            global_freq[nums[i]]++;
        }

        // 2. main loop 

        long long triplets = 0;

        for(int i = 0; i < n; i++){
            // 4. update the previous table frequency
            prev_freq[nums[i]]++;
            
            long long target = 2 * nums[i];
            
            // 1. check if target in prev
            if(prev_freq.find(target) != prev_freq.end()){ // target in prev table


                // 2. check global
                if(global_freq.find(target) != global_freq.end()){ // target in next table

                    // Get previous occurrences and calculate next occurrences

                    long long prev_count = prev_freq[target];
                    long long next_count = global_freq[target] - prev_count;

                    if(nums[i] == target) next_count = max(next_count - 1, 0LL);

                    // 3. make the addition

                    // --> thoughg we are using long long for all of them but still multiplication overflows long long as well 
                    // --> therefore we need to mod them before multiplication
                    triplets += (prev_count % MOD) * (next_count % MOD);
                    
                }
            }
        }

        return (int)(triplets % MOD);
        
    }
};

```