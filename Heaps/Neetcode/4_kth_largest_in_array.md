### My Code 


```cpp
class Solution {
public:
    int findKthLargest(vector<int>& nums, int k) {

        priority_queue< int, 
        vector<int>,
        greater <int>        
        > min_heap;

/*
1. either you have a min heap -- keep it of size k -- and for answer you have to pop ONLY TOP element  

2. You have a max heap -- keep it of n size -- and for answer you would need to pop k elements  
*/

        for (int num : nums){

            min_heap.push(num);
            if (min_heap.size() > k){
                min_heap.pop();
            }

        }

        return min_heap.top();
        
    }
};
```