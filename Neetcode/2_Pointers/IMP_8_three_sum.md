## Main Points:
1. Calculate ALL triplets
2. Return only unique triplets

## BRUTE: 3 Nested loops to check every triplet

```cpp


class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {

        set <vector<int>> unique_set;
        
        int n = nums.size();
        
        for (int i = 0; i < n; i++){
                
            for (int j = i + 1; j < n; j++){

                for (int k = j + 1; k < n; k++){

                    if (nums[i] + nums[j] + nums[k] == 0){

                        vector<int> triplet = {nums[i], nums[j], nums[k]};
                        sort(triplet.begin(), triplet.end());
                        unique_set.insert(triplet);
                    }
                }
            }
        }

        vector <vector<int>> result (unique_set.begin(), unique_set.end());

        return unique_result;
        
    }
};
```


## BETTER: Maybe we can use that "DIFF" logic which we have used for 2 Sum

- we can change i + j + k = 0   --to-->>  - (i + j) = k

#### Algo

```bash
BETTER: Maybe we can use that "DIFF" logic which we have used for 2 Sum
1. Nested loop for i and j 
2. if - (arr[i] + arr[j]) is FOUND IN <SET to-find-k>:
    - then make the triplet of ijk 
    - sort it 
    - add to result set
    - add arr[j] to <SET to-find-k>

3. If not found in <SET to-find-k>
    - add arr[j] to <SET to-find-k>

ADDITIONAL NOTE --> We need to empty the tofindk set at every iteration of i --> we can do this by reinitializing it everytime 
```


```cpp
class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {

        int n = nums.size();

        set <vector<int>> triplets;


        for (int i = 0; i < n; i++){
            
            
            set <int> set_to_find_k;


            for (int j = i+1; j < n; j++){

                int third = - (nums[i] + nums[j]);

                if (set_to_find_k.find(third) != set_to_find_k.end()){
                    // we found k 
                    vector <int> temp = {nums[i], nums[j], third};
                    sort (temp.begin(), temp.end());
                    triplets.insert(temp);
                }

                set_to_find_k.insert(nums[j]);                
            }
        }

        vector<vector<int>> result (triplets.begin(), triplets.end());

        return result;
    }
};
```




## OPTIMAL: 3 Pointer approach 

### Algo:

```
1. SORT THE ARRAY 
2. Set i at 0 | j at i+1 | k at end 
    - i would act constant --> and we would be finding sum of ijk --> if it is greater than 0 then k-- --> if less than 0 then j++

    - IMPORTANT POINT: when we increment j and k after not finding 0 -> we need to increment such that it CHNAGES THE REPRESENTING VALUE 

    Eg: 1,1,2 --> if j was on 1 then it should increment such that it GETS to 2 --> or else we would be testing the same combination again 


3. We are also supposed to increment i in the same fashion

4. Also when found the sum as 0 --> you can directly add the triplet of ijk in results becuase it willl be sorted already and it would be unique as well
```


```cpp
class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {

        vector <vector<int>> result;
        int n = nums.size();

        sort(nums.begin(), nums.end());

        for (int i = 0; i < n - 2; i++){

            // Skip duplicate values for i
            if (i > 0 && nums[i] == nums[i-1]) {
                continue;
            }

            int j = i + 1;
            int k = n - 1;

            while (j < k){

                int sum  = nums[i] + nums[j] + nums[k];

                if (sum > 0){
                    // need to reduce
                    k--;
                   
                   
                    // THOUGH we needed to skip the duplicates on failures as well --> we are not apparently doing that because it doe not matter I GUESS 

                    // int initial_k = nums[k];
                    // while(nums[k] == initial_k && j < k){
                    //     k--;
                    // }

                }
                else if (sum < 0){
                    // need to increase
                    j++;

                    // THOUGH we needed to skip the duplicates on failures as well --> we are not apparently doing that because it doe not matter I GUESS 


                    // int initial_j = nums[j];
                    // while(nums[j] == initial_j && j < k){
                    //     j++;
                    // }

                }
                else{
                    // found triplet
                    vector<int> temp = {nums[i], nums[j], nums[k]};
                    result.push_back(temp);

// IMPORTANT -->> This manual increment is VERY IMP because --> THIS HANDLES THE CASE WHERE IT HAS NO DUPLICATES --> hence as we would have incremented/decremented manually, the while cases below WOULD NOT TRIGGER 
                    j++;
                    k--;

                    while(nums[j] == nums[j-1] && j < k){
                        j++;
                    }

                    while(nums[k] == nums[k+1] && j < k){
                        k--;
                    }
            
                }
                
            }

        }

        return result;
    }
};
```