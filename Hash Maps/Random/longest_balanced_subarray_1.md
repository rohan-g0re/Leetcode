> 10th February 2026

## BRUTE --> apparently the only solution

### INTUITION

1. We can do a nested loop for considering all the subarrays
2. we use sets to keep on getting the count of distinct odd and even numbers
3. if we have a VALID BALANCED ARRAY --> then we update the max length count

## IMPORTANT TRICK --> Short Circuit the loop if there is no way you can get better max length in any upcoming trials

```cpp

class Solution {
public:
    int longestBalanced(vector<int>& nums) {

        int n = nums.size();
        int max_length = 0;


        for (int i = 0; i < n; i++){

            unordered_set<int> even;
            unordered_set<int> odd;


            for (int j = i; j < n; j++){


                if (nums[j] % 2 == 0) even.insert(nums[j]);
                else odd.insert(nums[j]);


                // it means that currently "i" and "j" represent a valid balanced array between them --> therefore update the max length
                if(odd.size() == even.size()){

                    max_length = max (max_length, j - i + 1);

                }


                // IMPORTANT --> we can also cut the upcoming loops --> if the max length has already reched the ceiling - such that with all the upcoming iterations, it can still not surpass the current max length. 

                if (max_length > n - i) return max_length;

            }
        }

        return max_length;
      
    }
};

```
