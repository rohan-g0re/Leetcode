## INTUITION

#### IMPORTANT --> a boat can carry at max two people at a time - Independent of the limit

1. sort the array --> we know that people[i] <= limit ------>>>> hence we can fit the largest person for sure 
2. There are only 2 conditions:
    1. heavist and lighest person go 
    2. only heaviest goes
3. Algo:
    - try to add both -if possible then good
    - if not then add heaviest 


#### CODE:

```cpp
class Solution {
public:
    int numRescueBoats(vector<int>& people, int limit) {

        sort(people.begin(), people.end());

        int l = 0;
        int r = people.size() - 1;
        int boats = 0;

        while(l <= r){

            // try if both fit
            if(people[r] + people[l] <= limit){
                boats++;
                l++;
                r--;
            }
            // both dont fit
            else{
                boats++;
                r--;
            }
        }
        return boats;
    }
};
```