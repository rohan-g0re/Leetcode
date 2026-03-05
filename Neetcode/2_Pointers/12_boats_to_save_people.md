## INTUITION
1. sort the array --> we know that people[i] <= limit ------>>>> hence we can fit the largest person for sure 
2. Algo:
    - keep on adding big people (people from right) UNTIL YOU CANT ADD MORE
    - if space remaining --> try smallest people (people from left)
    - if we cant fill anymroe from either ends --> BOAT IS DONE --> NEXT BOAT 


#### CODE:

```cpp
class Solution {
public:
    int numRescueBoats(vector<int>& people, int limit) {

        sort(people.begin(), people.end());
        int boats = 0;

        int n = people.size();
        int l = 0;
        int r = n - 1;

        while(l <= r){
            // once for a boat
            int weight = 0;
            int boat_count = 0;
            
            // 1st loop for adding heaviest people from right
            while(r > 0 && boat_count < 2 && weight + people[r] <= limit){
                weight += people[r];
                boat_count++;
                r--;
            }

            // 2nd loop for adding lightest people from left
            while(l < n && boat_count < 2 && weight + people[l] <= limit){
                weight += people[l];
                boat_count++;
                l++;
            }
            boats++;
        }

        return boats;      
    }
};
```