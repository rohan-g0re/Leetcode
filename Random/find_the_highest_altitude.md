
# LEETCODE 1732 - Easy



## INTUITION:
- simulation
- we cant find actual answer untill we calculate the complete movement

## BRUTE: 
1. construct the altitude array
2. keep a max variable which gets updated whenever altitde is more that it


## BETTER:
1. without the EXTRA array

#### C++ Code:

```cpp
class Solution {
public:
    int largestAltitude(vector<int>& gain) {


        int current = 0;
        int max = 0;
        
        for (int g : gain){

            // 1. add to current
            current += g;

            // 2. check if current > max --> if yes then update
            if(current > max){
                max = current;
            }
        }
        return max;
    }
};
```


#### Python Code --> this python does **NOT F'ING ALLOW** TYPE DECLARATIONS 



```python
class Solution:
    def largestAltitude(self, gain: List[int]) -> int:
        
        current = 0
        max_a = 0

        for g in gain:
            current += g

            if(current > max_a):
                max_a = current
        
        return max_a
```