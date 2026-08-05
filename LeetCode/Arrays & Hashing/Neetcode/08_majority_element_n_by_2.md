## INTUITIONS: 

1. The order does not matter - so we can play around with the sorting and reversing functions 
2. we somwhow need to get a hold of the count of items 
    2.1 It can either be finding element which has more count than n/2
    2.2 Or we can build logic such that we get numbers whose COMBINED count reaches n/2 --> which means that the other number has the majority count 
    2.3 these are basically the P(a) && 1 - P(a) approaches 

## BRUTE --> check every element and then count for it 

## BETTER --> have a freq_map 

*/

class Solution {
public:
    int majorityElement(vector<int>& nums) {

        unordered_map <int, int> freq_map;

        for (int num : nums){
            freq_map[num]++;
        }

        int threshold = nums.size() / 2;

        for (auto& pair : freq_map){
            if (pair.second > threshold){
                return pair.first;
            }
        }

        return 0;
        
    }
};


## OPTIMAL --> Moore's Voting Algorithm

```cpp

class Solution {
public:
    int majorityElement(vector<int>& nums) {
        
        int element = 0;
        int count = 0;

        // STEP 1: Moore's Voting Algorithm

        for (int num : nums){
            if (count == 0){
                element = num;
                count++;
            }
            else{ // count is not zero
                if (num == element){
                    count++;
                }
                else{
                    count--;
                }
            }
        }

        // We will finallly have a element at the end of voting algo

        // STEP 2:  NOW  we need to VERIFY if the ELEMENT is correct

        count = 0;

        for (int num : nums){
            if (num == element){
                count++;
            }
        }

        if (count > nums.size() / 2){
            return element;
        }
        return 0;
        
    }
};

```