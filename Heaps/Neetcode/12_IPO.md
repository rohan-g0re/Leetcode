

## BRUTE: Keep pushing in heap for finding best-fit task 


```cpp
/*

BRUTE:
// repeat this k times

// 1. collect all the <profit, capital> pairs where capital < w --> push all these pairs in max_heap --> push in format <profit/capital, index_of_capital> 

// can also use index_of_profits --> basically need to use some array as a visited array

// 2. pop from heap and --> add capital[i] in w and mark visited in profit and capital table

*/


class Solution {
public:
    int findMaximizedCapital(int k, int w, vector<int>& profits, vector<int>& capital) {
        


        for(int i = 0; i < k; i++){

            priority_queue <pair<int, int>> max_heap;
            
            
            // 1. pushed neccessary

            for(int i = 0; i < capital.size(); i++){
                if(capital[i] <= w){

                    max_heap.push({profits[i], i});
                }
            }

            if(max_heap.empty()) break; // if there was no valid element we need to stop the process and return w as it is

            // 2. pop best

            w += max_heap.top().first;
            capital[max_heap.top().second] = INT_MAX;
        }
        return w;
    }
};

```



## OPTIMIZED: Sort the array values wrt capital (by using a combined array)  so that you dont need to repeat traversals upon the array and can keep on pushing into the main heap (no need of re-initializing)  



#### IMPORTANT 1 --> `.size()` returns the value in dtype = `size_t`
#### IMPORTANT 2 --> `.min()` && `.max()` functions require both the variables in same datatype


```cpp


class Solution {
public:
    int findMaximizedCapital(int k, int w, vector<int>& profits, vector<int>& capital) {

        // if k greater than tasks availble then k should be at max tasks --> ACTUALLy it should always be at max `number of tasks`

        int a = min(k, (int)capital.size());
        


        vector<pair<int, int>> main_array;

        // 1.1 pushed in paired-array 

        for(int i = 0; i < profits.size(); i++){
            main_array.push_back({capital[i], profits[i]});
        }


        // 1.2 sort paired-array

        sort(main_array.begin(), main_array.end());

        priority_queue<int> max_heap;

        // major loop

        int mover = 0;


        for(int i = 0; i < k; i++){

            // increment mover until capital[mover] becomes invalid
            
            int mover_pre = mover;

            while (mover < main_array.size() && main_array[mover].first <= w){

                // keep pushing in heap

                max_heap.push(main_array[mover].second);

                mover++;
            }

            // ----> we have found the max profit for valid capital AT THE TOP OF MAX HEAP

            // if heap is empty then we dont have valid task --> else take top 

            if(!max_heap.empty()){ //which means we moved --> then increment
                w += max_heap.top();
                max_heap.pop();
            }
            else{ //we did not move --> hence no valid task left
                return w;
            }
        }
        return w;
    }
};


```