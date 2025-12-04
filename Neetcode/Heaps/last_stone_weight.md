

```cpp

class Solution {
public:
    int lastStoneWeight(vector<int>& stones) {
        
        priority_queue<int> max_heap;

        for (int num : stones){
            max_heap.push(num);
        }

        // now we play till empty

        while (!max_heap.empty()){

            if (max_heap.size() == 1) return max_heap.top();

            int y = max_heap.top();
            max_heap.pop();
            int x = max_heap.top();
            max_heap.pop();
            
            if (x == y){
                continue;
            }
            else{
                max_heap.push ( abs(y-x) );
            }
        }

        return 0;

    }
};

```