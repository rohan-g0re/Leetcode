
/*
BRUTE -> comparing each element and finding its count

BETTER 1 --> using hashmap as a frequency map


```cpp
class Solution {
public:
    vector<int> majorityElement(vector<int>& nums) {

        unordered_map <int, int> freq_map;

        for (int num : nums){
            freq_map[num]++;
        }

        int threshold = nums.size() / 3;
        vector <int> result; 

        for (auto& pair : freq_map){
            if (pair.second > threshold){
                result.push_back(pair.first);
            }
        }

        return result;

    }
};
```




## BETTER 2 --> hashmap but with only 1 iteration

```
- so basically when incrementing value we have to check if it has crossed the threshold or not

--> we do this by searching when it has SURELY CROSSED THRESHOOLD (hence +1 in threshold)

--> after this even if the number appears and the freq in map increases, we will never lookup in the map as we know that it has already been added to the solition 
```

#### ALSO THERE IS A VERY IMPORTANT STOPPING CONDITION --> if the size of the resultant vector reaches 2 WE STOP --> becasue there cannot be more than 2 numbers that satisfy this condition --> the only options are [0, 1, 2] 



```cpp
class Solution {
public:
    vector<int> majorityElement(vector<int>& nums) {

        unordered_map <int, int> freq_map;
        int threshold = nums.size() / 3 + 1;
        vector <int> result; 

        for (int num : nums){
            freq_map[num]++;

            if (freq_map[num] == threshold){
                result.push_back(num);

                if (result.size() == 2) break;
            }
        }

        return result;

    }
};
```




# OPTIMAL --> MODIFIED Moore's Voting Algorithm

### CODE

```cpp
class Solution {
public:
    vector<int> majorityElement(vector<int>& nums) {

        int count1 = 0, count2 = 0;
        int ele1 = INT_MIN;
        int ele2 = INT_MIN;

        for (int num : nums){

            // RESETTING PART 

            if (count1 == 0 && num != ele2){
                ele1 = num;
                count1 = 1;
            }
            else if (count2 == 0 && num != ele1){
                ele2 = num;
                count2 = 1;
            }
            
            // INCREMENTING PART 

            else if (num == ele1) count1++;
            else if (num == ele2) count2++;


            // DECREMENTING PART 

            else {
                count1--;
                count2--;
            }
        }


        // When all the above is done we will have 2 elements --> now we need to verify their count

        count1 = 0, count2 = 0;

        for (int num : nums){
            if (num == ele1){
                count1++;
            }
            else if(num == ele2){
                count2++;
            }
        }

        vector <int> result;
        int threshold = nums.size() / 3;

        if (count1 > threshold) result.push_back(ele1);
        if (count2 > threshold) result.push_back(ele2);

        return result;

    }
};
```