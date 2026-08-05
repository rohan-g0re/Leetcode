
## Testing 3 different cases with examples: odd-odd, even-even, odd-even.

```bash

O O  --> (high - low)/2 + 1
3 - 11

579

5 - 9

11 - 19 = 5
11 13 15 17 19

------------------
E E --> (high - low)/2

4 - 8 
2

10 - 20 

------------

O E --> (high - low)/2 + 1 

5 10

8 - 17

9 11 13 15 17


```

## CODE:

class Solution {
public:
    int countOdds(int low, int high) {

        if((low % 2 == 0 && high % 2 != 0) ||(low % 2 != 0 && high % 2 == 0) || (low % 2 != 0 && high % 2 != 0)){
            return (high-low)/2 + 1;
        }
        
        return (high - low) / 2;
        
    }
};