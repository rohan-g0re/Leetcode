## Binary Search Code

```cpp

class Solution {
public:
    int search(vector<int>& nums, int target) {

        int low = 0; 
        int high = nums.size() - 1;

        while (low <= high){

            int mid = low + (high - low / 2);

            if (nums[mid] == target){
                return mid;
            }
            else if (nums[mid] > target){
                high = mid - 1;
            }
            else{
                low = mid + 1;
            }
        }

        return -1;
        
    }
};

```

## Similar Question as example: Quess higher or lower

```cpp

/** 
 * Forward declaration of guess API.
 * @param  num   your guess
 * @return 	     -1 if num is higher than the picked number
 *			      1 if num is lower than the picked number
 *               otherwise return 0
 * int guess(int num);
 */

class Solution {
public:
    int guessNumber(int n) {

        int low = 1;
        int high = INT_MAX;

        while(low <= high){
            int mid = low + (high - low) / 2;

            int result = guess(mid);

            if(result == -1){
                high = mid - 1;
            }
            else if(result == 1){
                low = mid + 1;
            }
            else{ // found
                return mid;
            }
        }

        return -1;
        
    }
};
```