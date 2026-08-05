## INTUITION: 
#### direclty starting with stage 4 of DP which is space optimized tabulation 

- We need:

    - zero --> T0 --> T(n)
    - one --> T1 --> T(n+1)
    - two --> T2 --> T(n+2)
    - current --> T3 --> T(n+3)


```cpp
class Solution {
public:
    int tribonacci(int n) {
        
        int zero = 0;
        int one = 1;
        int two = 1;

        if(n == 0) return zero;
        if(n <= 2) return one;

        int current = 0;
        for(int i = 3; i <= n; i++){

            // 1. calculate current;

            current = zero + one + two;

            // 2. update values

            zero = one;
            one = two;
            two = current;

        }
        return two;
    }
};

```