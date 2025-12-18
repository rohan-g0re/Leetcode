## INTUITION:
1. We need to preserve the order
2. Does having duplicates make any change
3. Check every pair

#### MEMORY:
1. We had used a "DIFF" method before --> which basically searched for the
remaining value in a map --> and returned a bool

## Attempt 1: Use a map and store like (number, index)
    Limitation: this would use O(n) space which is not permitted

## BRUTE: Check every sub pair in O(n^2)

## BETTER: 
- we SOMEHOW need to use the sorted order to our advantage 
- other things to remember --> onstant extra space, preserve indexes

--->>>>

1. Intialize 2 pointers - start and end
2. if curr_sum < target --> we need to "Bring in a bigger num to increase the sum" --> thats why l++
3. if curr_sum > target --> we need to "Bring in a smaller number to reduce the sum" --> thats why r--

```cpp

class Solution {
public:
    vector<int> twoSum(vector<int>& numbers, int target) {
        
        int start = 0;
        int end = numbers.size() - 1;

        while (start < end){
            if (numbers[start] + numbers[end] < target){
                start++;
                continue;
            }
            else if (numbers[start] + numbers[end] > target){
                end--;
                continue;
            }
            return {start + 1, end + 1};
        }

        return {};

    }
};
```