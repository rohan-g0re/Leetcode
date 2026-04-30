## INTUITION --> the two closest elements will be the one immediate to the right and left
- find them and break
- compare their distance

```cpp
class Solution {
public:
    int getMinDistance(vector<int>& nums, int target, int start) {

        // 1. find the target in [0..start] by i--
        int left = INT_MAX;
        for(int i = start; i >= 0; i--){
            if(nums[i] == target){
                left = i;
                break;
            }
        }
        // 2. find the target in (start...n] by i++
        int right = INT_MAX;
        for(int i = start+1; i < nums.size(); i++){
            if(nums[i] == target){
                right = i;
                break;
            }
        }
        // 3. if both are non-inf then compare and return

        if(left < INT_MAX && right < INT_MAX){
            return min(abs(left-start), abs(right-start));
        }

        else{
            if(left < INT_MAX) return abs(left - start);
            else return abs(right - start);
        }
        return 69;
    }
};

```