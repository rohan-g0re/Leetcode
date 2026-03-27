## Approach 1: Binary Search:

### INTUITION --> We want to count how many numbers belong to the range [1, mid] , i.e., numbers that are at most `mid`

1. Use binary search on the space and get a mid
2. for every mid check if there are exactly those many numbers in the array less than that
3. IF there are less than mid then it means the duplicates is from **RIGHT side** of space --> if there are more, the duplicates are in the **LEFT side** of space


```cpp
class Solution {
public:
    int findDuplicate(vector<int>& nums) {

        int start = 1;
        int end = nums.size() - 1;

        while(start < end){

            int mid = start + (end - start) / 2;

            int cnt = 0;
            for(int num: nums){
                if(num <= mid)cnt++;
            }

            if (cnt <= mid) start = mid + 1;
            else end = mid;

        }

        // we can return start --OR-- end because they are in the same position
        return start;

    }
};
```

#### Time Complexity = O(n * log n)




## Approach 2: Linked List Cycle Detection (Floyd's Tortoise and Hare)

### INTUITION --> Treat indexes `i` as memory address pointers --> HENCE: `nums[i]` becomes the equivalent of `next` in a linked list. --> [Neetcode Video](https://www.youtube.com/watch?v=wjYnzkAhcNk)

#### PASS 1
- Find the `intersection point` of slow and fast pointers within the Linked Lists.

#### PASS 2
- Start with a pointer at head of the LL (array's start) && another pointer at `intersection point`
- move both of them --> **one step at a time until they meet**.
- The meeting point will be the duplicate number.

#### Time Complexity = O(n)
