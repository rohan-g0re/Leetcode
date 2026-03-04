
## Approach 1: O(n + n*log n) --> add nums 2 to nums 1 and sort

## Approach 2: O (m + n) but uses extra O(m+n) space


```cpp

class Solution {
public:
    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {

        vector<int>result;

        int l = 0;
        int r = 0;

        while(l < m && r < n){
            if (nums1[l] <= nums2[r]){
                result.push_back(nums1[l]);
                l++;
                continue;
            }
            else{
                result.push_back(nums2[r]);
                r++;
            }
        }

        // copy if nums 1 is longer
        
        while(l < m){
            result.push_back(nums1[l]);
            l++;
        }
        
        // copy if nums 2 is longer
        
        while(r < n){
            result.push_back(nums2[r]);
            r++;
        }
        
        nums1 = result;      
    }
};

```


## Approach 3: O (m+n) without extra space --> filling nums 1 in reverse by greatest element first

```cpp
class Solution {
public:
    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {

        int l = m-1;
        int r = n-1;

        int write_pointer = m + n - 1;

        while(l >= 0 && r >= 0){
            if (nums1[l] >= nums2[r]){
                nums1[write_pointer] = nums1[l];
                l--;
            }
            else{
                nums1[write_pointer] = nums2[r];
                r--;
            }
            write_pointer--;
        }
        // if nums 1 is longer --> we dont need to copy elements as they are already there
        
        // if nums 2 is longer --> we need to copy elements

        while(r >= 0){
            nums1[write_pointer] = nums2[r];
            write_pointer--;
            r--;
        }
    }
};
```