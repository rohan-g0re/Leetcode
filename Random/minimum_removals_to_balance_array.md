# Recursion / Dumb DP --> TLE: Time Limit Exceeded

```cpp

class Solution {

private:

int rec_func(vector<int>& nums, int& k, int min_index, int max_index, int current_removals){

    // 1. base conditions
        // 1.1 failure --> reached size 1 of array  
        if (min_index == max_index) return current_removals;

        // 1.2 success
        if (nums[max_index] <= k * nums[min_index]) return current_removals;


    // if not then basically we have to recurse into removing from either ends


    // 2. recursion logic --> remove minimum OR remove maximum

    int r_min = rec_func(nums, k, min_index + 1, max_index, current_removals + 1);

    int r_max = rec_func(nums, k, min_index, max_index - 1, current_removals + 1); 


    // 3. return logic

    return (min(r_min, r_max));


}

public:
    int minRemoval(vector<int>& nums, int k) {

        int n = nums.size();

        if (n == 1) return 0;

        sort(nums.begin(), nums.end());

        return rec_func(nums, k, 0, n-1, 0);
        
    }
};

```



# Recursion with Memoization --> MLE: Memory limit Exceeded

```cpp

class Solution {

private:

int rec_func(vector<int>& nums, int& k, int min_index, int max_index, int current_removals, vector<vector<int>>& dp_table ){

    // 1. base conditions
        // 1.1 failure --> reached size 1 of array  
        if (min_index == max_index) return current_removals;

        // 1.2 success

        double product = k * (double)nums[min_index];
        if (nums[max_index] <= product) return current_removals;


    // if not then basically we have to recurse into removing from either ends

    // 1.3 before exploration -->check if we have that in table
    if (dp_table[min_index][max_index] != -1) return dp_table[min_index][max_index];


    // 2. recursion logic --> remove minimum OR remove maximum

    int r_min = rec_func(nums, k, min_index + 1, max_index, current_removals + 1, dp_table);

    int r_max = rec_func(nums, k, min_index, max_index - 1, current_removals + 1, dp_table); 


    // 3. return and memoization logic

    dp_table[min_index][max_index] = min(r_min, r_max);

    return dp_table[min_index][max_index];


}



public:
    int minRemoval(vector<int>& nums, int k) {

        int n = nums.size();

        if (n == 1) return 0;


        sort(nums.begin(), nums.end());

        vector <vector <int>> dp_table (n, vector<int>(n, -1));

        return rec_func(nums, k, 0, n-1, 0, dp_table);
        
    }
};
```

# Tabulation Attempt 1 with calculation formulation --> MLE: Memory Limit Exceeded.

```cpp

class Solution {

public:
    int minRemoval(vector<int>& nums, int k) {

        int n = nums.size();
        if (n == 1) return 0;

        sort(nums.begin(), nums.end());
        vector <vector <int>> dp_table (n, vector<int>(n, -1));

        /*
        1.1 base condition handling 

        if the indexes match --> it should return a count
        the indexes can only match when both of them have collectively removed ALL OTHER ELEMENTS FROM ARRAY --> which means they have removed n-1 elements --> therefore all the instances in the table can be filled using this logic
        */

        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){
                if (i == j) dp_table[i][j] = n-1;                
            }
        }


        int global_min = n-1;


        for (int min_index = 0; min_index < n; min_index++){
            
            int max_index = min_index + 1;

            for (; max_index < n; max_index++){


                // 1. VALID INDEXES FOUND SUCH THAT ARRAY WILL BE BALANCED

                if (nums[max_index] <= k * (double)nums[min_index]){
                    
                    dp_table[min_index][max_index] = (n-1) - max_index + min_index;
                    global_min = min (global_min, dp_table[min_index][max_index]);

                }

                // 2. INDEXES THAT DONT GIVE BALANCED ARRAY --> just copy the previous thing

                else{                    
                    
                    dp_table[min_index][max_index] = dp_table[min_index][max_index - 1];
                }
            }
        }
        return global_min;
    }
};

```


# Tabulation attempt 2 with carry forwarding table values --> MLE: Memory Limit Exceeded.

```cpp

class Solution {

public:
    int minRemoval(vector<int>& nums, int k) {

        int n = nums.size();

        if (n == 1) return 0;


        sort(nums.begin(), nums.end());

        vector <vector <int>> dp_table (n, vector<int>(n, -1));


        /*
        1.1 base condition handling 

        if the indexes match --> it should return a count
        the indexes can only match when both of them have collectively removed ALL OTHER ELEMENTS FROM ARRAY --> which means they have removed n-1 elements --> therefore all the instances in the table can be filled using this logic
        */

        for (int i = 0; i < n; i++){
            for (int j = 0; j < n; j++){
                if (i == j) dp_table[i][j] = n-1;                
            }
        }


        int global_min = n-1;


        for (int min_index = 0; min_index < n; min_index++){
            
            int max_index = min_index + 1;

            for (; max_index < n; max_index++){


                // 1. VALID INDEXES FOUND SUCH THAT ARRAY WILL BE BALANCED

                if (nums[max_index] <= k * (double)nums[min_index]){
                
                /*As we know that we will always be starting from one cell after the diagonal element so if there is an improvement we can decrement the removals. If it is not valid then we can keep it the same.*/

/*CHANGE--->*/      dp_table[min_index][max_index] = dp_table[min_index][max_index - 1] - 1;
                    global_min = min (global_min, dp_table[min_index][max_index]);

                }

                // 2. INDEXES THAT DONT GIVE BALANCED ARRAY --> just copy the previous thing

                else{                    
                    
                    dp_table[min_index][max_index] = dp_table[min_index][max_index - 1];
                }
            }
        }
        return global_min;
    }
};

```


# 2 pointer Approach --> TLE 

```cpp

class Solution {

public:
    int minRemoval(vector<int>& nums, int k) {

        int n = nums.size();
        if (n == 1) return 0;
        sort(nums.begin(), nums.end());

        int global_min = n-1;

        for (int min_index = 0; min_index < n; min_index++){            
            for (int max_index = min_index + 1; max_index < n; max_index++){

                // 1. VALID INDEXES FOUND SUCH THAT ARRAY WILL BE BALANCED
                if (nums[max_index] <= k * (double)nums[min_index]){
                    global_min = min (global_min, (n-1) - max_index + min_index);
                }

                // 2. INDEXES THAT DONT GIVE BALANCED ARRAY --> nay next value is not going to give value hence break
                else{                    
                    break;
                }
            }
        }
        return global_min;
    }
};

```

# 2 pointer / Sliding window-like approach

## KEY INSIGHTS:

### In a sorted fashion, if one max_index fails, then all upcoming max_indexes will be failing, and hence we don't need to check those and can directly move to the next minimum_index.

### We don't need to reset right back to left+1. We can keep right where it is and just move left!


```cpp


class Solution {

public:
    int minRemoval(vector<int>& nums, int k) {

        int n = nums.size();
        if (n == 1) return 0;
        sort(nums.begin(), nums.end());

        int min_removals = n-1;

        int max_index = 1;
        
        
        for (int min_index = 0; min_index < n; min_index++){            

            // 1. VALID INDEXES FOUND SUCH THAT ARRAY WILL BE BALANCED
            while (max_index < n && nums[max_index] <= k * (double)nums[min_index]){
                    max_index++;
            }

            // 2. When the pattern falls off --> we note the total removals needed to achieve this config
            // notice that I changed from (n-1) --> (n) because exiting from while loop increments the max_index by 1

            min_removals = min (min_removals, n - max_index + min_index);

            // this allows us to update the minimum pointer without resetting the value of the max pointer
        
        }
        
        // we could have also calculate max length in the process and returned (n - max_length)
        return min_removals;
    }
};


```