## listed all the 2 comparisons and 4 results:
```bash
1. Compare mid to last  

    1.1 mid < last  
        - mid in sorted part  
        - update mid  
        - check left  

    1.2 mid > last  
        - mid in rotated part
        - update mid  
        - check right  

2. Compare mid to low  

    2.1 mid > low  
        - mid in sorted part  
        - update mid  
        - search left  

    2.2 mid < low  
        - mid’s left is unsorted which can have smaller  
        - update mid  
        - search left  

Search left vs search right  
- Search left: 1.1, 2.1, 2.2  
- Search right: 1.2

```

```cpp

class Solution {
public:
    int findMin(vector<int>& nums) {

        int l = 0;
        int r = nums.size() - 1;

        int ans = INT_MAX;

        while (l <= r){

            int mid = (l + r) / 2;
            
            // mid is in sorted portion
            if (nums[mid] <= nums[r]){
                ans = min(ans, nums[mid]);
                r = mid - 1;
            }

            // mid is in rotated part --> min will be in rotated part ahead, so we update answer value and move to the right towards the sorted part
            else{
                ans = min (ans, nums[mid]);
                l = mid + 1;
            }

        }
        return ans;

    }
};

```