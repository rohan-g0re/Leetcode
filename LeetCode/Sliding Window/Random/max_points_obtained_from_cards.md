# LC 1423 - Medium


## INTUITION:
- the left sum is going to be of first m elements
- the right sum is going to be of last n elements
- REMEMBER --> m + n = k

### Process:
1. calculate the left sum for m = k elements
2. keep reducing m and increasing n at the same time to take into account all the possible subarrays

```cpp


class Solution {
public:
    int maxScore(vector<int>& cardPoints, int k) {

        int left_sum = 0;
        int right_sum = 0;
        int max_points = 0;

        //calculate forward sum for left side
        for(int i = 0; i < k; i++){
            left_sum += cardPoints[i];
        }

        max_points = left_sum; // did not do this in above for loop bcoz adding value makes it greater --> SINCE WE ONLY HAVE POSITIVE NUMBERS IN ARRAY 

        int l = k -1;
        int r = cardPoints.size() - 1;

        while(l >= 0){
            
            // decrement l_sum and l
            left_sum -= cardPoints[l];
            l--;

            // increment r_sum and r
            right_sum += cardPoints[r];
            r--;

            // check if current config has max points
            max_points = max(max_points, left_sum + right_sum);
        }

        return max_points;
    }
};

```


# Complexities:
- TC = O (2 * k)
    - since the for loop and while loop run for only k iterations

- SC = O(1) - constant space since only variablesa used