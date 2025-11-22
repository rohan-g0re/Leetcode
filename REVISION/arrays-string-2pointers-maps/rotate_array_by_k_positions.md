## INTUITION
- no specific order (ascending/descending)
- also we have -ve numbers

## FAILED:  Attempt 1: 2 pointer approach 
```
--> set the pointers on 0 and n - k -1
--> keep on swapping

--> FUCKING HELL --> i am diong swapping --> BUT EVERY OTHER ELEMENT NEEDS TO MOVE
```

## INTUITIONS:
#### 1. we can maybe use an extra array to place the number
#### 2. for any method we choose we MIGHT NEED TO USE THE mod % operator FOR THE SHIFT because it should not get out of bounds  



## SOLUTION 1 --> Use extras array to put every element to in the correct place

```cpp
class Solution {
public:
    void rotate(vector<int>& nums, int k) {

        int n = nums.size();

        vector<int> final_array(n);
        // we create the vector of the same size so that the code works  --> && TO BE MORE SPECIFIC

        
        for (int i = 0; i < n; i++){

            int posi_after_shift = ( i + k ) % (n);
            // we are using modulo so that the final_posi should not get out of bounds

            final_array[posi_after_shift] = nums[i];
        }

        nums = final_array;

        
    }
};
```

### LEARNINGS

1. **To wrap around we always use %n**
2. BUT THIS IS STILL NOT IN-PLACE


## BRUTE INTUITION for IN-PLACE:
```
- we will perform k iterations over the array --> in each iteration we shift
elements ahead by 1
- have 2 temp variables temp1, temp2

update in 3 steps:
    1. temp1 = nums[i]
    2. nums[i] = temp2;
    3. temp2 = temp1
```

```cpp
class Solution {
public:
    void rotate(vector<int>& nums, int k) {

        int n = nums.size();

        for (int i = 0; i < k; i++) {

            int temp1 = 0;
            int temp2 = nums[n - 1];

            for (int i = 0; i < n; i++) {
                temp1 = nums[i];
                nums[i] = temp2;
                temp2 = temp1;
            }
        }
    }
};
```


##### Cleaner code snippet 

```cpp

class Solution {
public:
    void rotate(vector<int>& nums, int k) {

        int n = nums.size();

        for (int i = 0; i < k; i++) {

            int last = nums[n - 1];

            for (int i = n - 1; i > 0; i--) {
                nums[i] = nums[i - 1];
            }
            nums[0] = last;
        }
    }
};

```

**BUT THIS IS VERY EXPENSIVE - as we are having O(n^2) --> hence giving TLE**


## OPTIMAL INTUITION for IN-PLACE --> 3 reversals :
```
1. reverse the array 
2. reverse first k elements
3. reverse last n-k elements
```

```cpp
class Solution {
public:
    void rotate(vector<int>& nums, int k) {

        int n = nums.size();
        
        // need to explicitly hadle this case before getting intoi stuff
        k = k % n;

        int l = 0;
        int r = n-1;
        while (l < r){
            swap(nums[l], nums[r]);
            l++;
            r--;
        }
        
        l = 0;
        r = k - 1;
        while (l < r){
            swap(nums[l], nums[r]);
            l++;
            r--;
        }
        
        l = k;
        r = n-1;
        while (l < r){
            swap(nums[l], nums[r]);
            l++;
            r--;
        }

    }
};
```