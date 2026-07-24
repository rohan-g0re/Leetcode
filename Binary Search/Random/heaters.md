# Leetcode 475 - Heaters

## BRUTE --> for every house - find closest heater on both sides using binary search

1. INTUITION --> use lower bound to get the RHS heater
2. the heater before that, is going to be the LHS heater


```cpp
class Solution {
private:
    int lb(vector<int>& heaters, int target){

        sort(heaters.begin(), heaters.end());

        int start = 0;
        int end = heaters.size() - 1;
        int result = -1;

        while(start <= end){

            int mid = start + (end - start) / 2;

            // check ih heater at posi is valid?
            if(heaters[mid] >= target){
                result = mid; // this is the answer right now --> document it --> try for tighter answer
                end = mid - 1;
            }
            else{
                // less than target
                start = mid + 1;
            }
        }
        return result;
    }

public:
    int findRadius(vector<int>& houses, vector<int>& heaters) {

        long result = 0;

        for(int house : houses){

            int idx = lb(heaters, house);

            // idx can be valid or -1 if no right heater

            // --------- distance calculation ----------

                // 1. right part 

            long right_dist = LONG_MAX;
            if(idx != -1){
                right_dist = abs((long)house - (long)heaters[idx]);
            }



            // --------- left part -----------
            long left_dist = LONG_MAX;
            int left_index;
    
    
            //index calculation
            
            if(idx == -1){
                // it means that we did not find RHS heater --> which means the righmost heater is  actually the LHS heater
                left_index = heaters.size() - 1;
            }
            else{
                // we have some index --> now we need to check if 'idx - 1' is still in bound
                left_index = idx - 1;
            }


            // distance calc.
                
            if(left_index >= 0){
                left_dist = abs((long)house - (long)heaters[left_index]);
            }            
            


            // the min distance between these heaters is valid for this HOUSE --> but the final answer will be MAX of all these minimums

            long best_for_this_house = min(right_dist, left_dist);

            result = max(result, best_for_this_house);

        }

        return (int)result;
        
    }
};

```