## INTUITION: we cant sort because we need to preserve indexes

## Approach 1: BRUTE
1. n2 loop for testing all the pairs

## Approach 2: BRUTE with short circuit --> only testing the pairs which give i - j <= k
- **Still if k = n  then the time complexity is basically O(n^2)**


```cpp
class Solution {
public:
    bool containsNearbyDuplicate(vector<int>& nums, int k) {

        int n = nums.size();
        int i = 0;
        
        // edge case 1 --> k > n
        int j = k;
        if (j > n-1) j = n-1;

        while (i < j){

            // compare every number with i 

            for(int z = i+1; z <= j; z++){
                if (nums[z] == nums[i]) return true;
            }

            i++;

            // edge case 2 --> WINDOW SIZE will keep decreasing after j hits end and i still increments;
            if (j != n-1)j++;
        }
        return false;
    }
};
```


## Approach 3: KEEP WINDOW DETAILS IN MEMORY (set)
## Intuition

Imagine you are walking down a long street looking at house numbers. You want to know if you see the same house number twice, but only if the two houses are close to each other (within `k` steps).

**Constraint:**  
You have a "short-term memory" that can only hold `k` numbers.

**The Process:**

- As you walk past a house, you check your memory: "**Have I seen this number recently?**"
    - If yes, you shout "Found it!" (`return True`).
    - If no, you memorize this new number.
- **Crucial Step:** If your memory gets too full (more than `k` numbers), you "forget" the oldest number you saw to make room for new ones.

This concept of maintaining a fixed-size range as you move forward is called a **Sliding Window**.

---

## Approach

We use a **Hash Set** to represent this "sliding window" or "short-term memory".

1. **Initialize a Set:**  
   Create an empty set called `window`. This will store the elements currently in our range.

2. **Iterate:**  
   Loop through the array `nums` one by one using index `i`.

3. **Check for Duplicate:**  
   Before adding `nums[i]`, check if it is already in the `window` set.
    - If it is, it means we saw this number recently (within the last `k` indices), so **return `True`**.

4. **Add to Window:**  
   Add `nums[i]` to the set.

5. **Maintain Window Size:**  
   Check if the size of the set is now greater than `k`.
    - If it is, we must remove the element that is now too far away. That element is located at `nums[i - k]`.
    - Removing it ensures our set only checks numbers within the valid distance.

6. **Finish:**  
   If the loop finishes without finding a match, return `False`.

---

## Complexity

- **Time complexity:** `O(N)`
- **Space complexity:** `O(min(N, k))`


## Code:

```cpp
class Solution {
public:
    bool containsNearbyDuplicate(vector<int>& nums, int k) {

        int n = nums.size();

        unordered_set <int> window;

        for(int i = 0; i < n; i++){
            
            // 1. remove in valid number before comparing
            if (window.size() > k) window.erase(nums[i - k - 1]);

            // 2. compare the current number with set
            if (window.find(nums[i]) != window.end()) return true;
            
            // 3. insert this number in set
            window.insert(nums[i]);
        }

        return false;
        
    }
};
```