## INTUITION:
1. h will always be greater than the total number of piles
2. Lowest number we can go is total_sum / h

ALGO: 
1. Whenever we find mid as a valid answer, lower it down
2. **the extra function added APPLIES THE RESTRICTION OF PILES** -- if finished, need to wait for the hour --> if this wasnt here then lowerbound would have been the answer - WHICH IS WRONG 

### APPROACH 1: Using the range from 1 --> Max value of a pile 

```cpp

class Solution {

private: 

    bool solution(vector<int>& piles, int h, int mid){

        int time = 0;
        
        for(int i = 0; i < piles.size(); i++){

            int current_pile = piles[i];

// DIVIDE THE PILE to get the total hours required to finfish the pile
// Also use celing logic so that it does not floor the division value

            time += (current_pile + mid - 1) / mid;

            if (time > h) return false;
        }

        return true;

    }

public:
    int minEatingSpeed(vector<int>& piles, int h) {

        // sum
        int low = 1;
        // max
        int high = 0;

        for (int num : piles){
            high = max (high, num);
        }

        int current_lowest_k = high;

        while(low <= high){

            int mid = (low + high) / 2;

            if (solution(piles, h, mid)){
                current_lowest_k = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }

        return current_lowest_k;

    }
};

```


### Approach 2: Range is sum/h --> max pile

```cpp
class Solution {

private: 

    bool solution(vector<int>& piles, int h, int mid){

        int time = 0;
        
        for(int i = 0; i < piles.size(); i++){

            int current_pile = piles[i];

            time += (current_pile + mid - 1) / mid;

            if (time > h) return false;
        }

        return true;

    }

public:
    int minEatingSpeed(vector<int>& piles, int h) {

        // sum
        long long sum = 0;
        // max
        int high = 0;

        for (int num : piles){
            sum += num;
            high = max (high, num);
        }

        int low = (sum + h - 1) / h;
        // if (low < 1) low = 1;

        int current_lowest_k = high;

        while(low <= high){

            int mid = (low + high) / 2;

            if (solution(piles, h, mid)){
                current_lowest_k = mid;
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }

        return current_lowest_k;

    }
};

```



## SYNTAX LEARNINGS
#### to get a ceiling division for a/b --> do --> (a + b - 1) / b