## INTUITION:
1. we need to traverse through array
2. we cant sort as the position is important


# BRUTE --> Check EVERY sub array for their product
- have i an j as bounding indexes
- run between i an j to calculate prodduct
- compare it ot global_max



# BETTER --> Running product for j
- instead of 3 loops we can use 2 loops by having


```cpp
class Solution {
public:
    int maxProduct(vector<int>& nums) {

        int n = nums.size();
        if (n == 1)
            return nums[0];

        int global_max = INT_MIN;

        for (int i = 0; i < n; i++) {
            int current_product = 1;
            for (int j = i; j < n; j++) {

                current_product *= nums[j];

                if (current_product > global_max) {
                    global_max = current_product;
                }
            }
        }

        return global_max;
    }
};
```
**this is still O(n^2) --> need to bring it down somwhow**



# OPTIMAL --> splitting at -ve s and using prefix and suffix to find product of either sides && Restarting product calculation when gpt zeroes, which is basically splitting the array at zeroes 


## INTUITIONS:
- we need to DODGE negatives and zeroes

```
## 2 main things:
1. we basically SPLIT THE ARRAY upon ZEROES
2. IN EVERY SPLITED Subarray - we wind the max such that --> it is either going
to be a prefix or a suffix product --> this also takes into account the fact
that prefix and suffix include complete arrays as well

--> which means at any time --> we compare the max of prefix and suffix with
global_max


### Also instead of iterating 2 times we can do prefix nd suffix in one go
```

## OPTIMAL CODE

```cpp
class Solution {
public:
    int maxProduct(vector<int>& nums) {

        int n = nums.size();

        int global_max = INT_MIN;
        int prefix = 1;
        int suffix = 1;

        for (int i = 0; i < n; i++) {

            if (prefix == 0)
                prefix = 1;
            if (suffix == 0)
                suffix = 1;

            // this is how me start again from scratch on the side where we got a zero

            prefix *= nums[i];
            suffix *= nums[n - i - 1];

            global_max = max(global_max, max(prefix, suffix));
        }

        return global_max;
    }
};
```