## INTUITION --> SEACH IN STATE SPACE


```cpp
class Solution {
public:
    int mySqrt(int x) {

        int start = 1;
        int end = x;
        int mid = 0;
        int result = x;

        while(start <= end){
            mid = start + (end - start) / 2;
            
            double square = pow(mid, 2); // 1. use double because (2^31)^2 will go out of bound for int 

            if( square > x){
                end = mid - 1;
            }
            else if(square < x){
                start = mid + 1;
                result = mid; // 2. We are recording value as the formula calculates the "CEIL" --> and we need "FLOOR"
            }
            else{
                return mid;
            }
        }
        return result;
    }
};
```