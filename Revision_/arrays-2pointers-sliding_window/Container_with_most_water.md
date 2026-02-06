You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]).

Find two lines that together with the x-axis form a container, such that the container contains the most water.

Return the maximum amount of water a container can store.

Notice that you may not slant the container.

Input: height = [1,8,6,2,5,4,8,3,7]
Output: 49
Explanation: The above vertical lines are represented by array [1,8,6,2,5,4,8,3,7]. In this case, the max area of water (blue section) the container can contain is 49.


****************


## Intuition
- we dont just need tallest pillars - but we also need them to be furter away from each other -->> basically largets AREA
- area = l x h -->> 
    - l = j - i
    - h = min (height[i], height[j])


## Brute Force
- Run through every combination of i and j and calculate the max area 

```
class Solution {
public:
    int maxArea(vector<int>& height) {

        int max_area = 0;
        int n = height.size();

        for (int i = 0; i < n; i++){
            for (int j = i + 1; j < n; j++){
                
                int L = j - i;
                int H =  min (height[i], height[j]);
                int local_area = L * H;

                max_area = max (max_area, local_area);

            }
        }

        return max_area;

        
    }
};
```

GAVE A TLE;


## Approach 2 - 2 pointer


1. L = 0, R = n-1
2. We calculate area for the current config of L and R
3. then we shift THAT pointer which is minimum - between L and ----------
    - this is done in the hope that we find a bigger height which increases our area - though as we are moving we are reducing the length 


```
class Solution {
public:
    int maxArea(vector<int>& height) {

        int max_area = 0;
        int n = height.size();
        int L = 0;
        int R = n - 1;

        while (L <= R){

            int length = R - L;
            int z_height =  min (height[L], height[R]);
            int local_area = length * z_height;

            max_area = max (max_area, local_area);

            if ( height[L] < height[R]){
                L++;
            }
            else{
                R--;
            }
        }

        return max_area;
        
    }
};
```
