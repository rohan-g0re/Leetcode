# LC 621 - Medium 


## INTUITION:
- Execute tasks that have the most frequency 
- each task has same cooldown 
- each task has 1 unit execution time

#### WHAT DOES EACH STRUCTURE SIGNIFY?
- **HEAP** --> tasks that are **READY to schedule right now** (sorted by remaining freq)
- **QUEUE** --> tasks that are on **COOLDOWN** --> each entry = `{remaining_freq, time when it becomes ready again}`

```cpp

// heap <freq>

// queue <freq, cooldown>

class Solution {
public:
    int leastInterval(vector<char>& tasks, int n) {

        priority_queue<int> max_heap;

        queue <pair<int, int>> queue;

        // step 0 : push frequencies to heap 

        unordered_map <char, int> freq_map;

        for(char a : tasks){
            freq_map[a]++;
        }
      
        for (auto pair : freq_map){
            max_heap.push(pair.second);
        }

        // MAIN Step : until heap && QUEUE is empty --> because There can be a time when heap is empty but this means that nobody is ready and hence IDLE
        int time = 0;


        while (!max_heap.empty() || !queue.empty()){
            // this allows us to have heap empty but keep on going


            // STEP 1: if valid node in queue add it in heap

            if (!queue.empty() && queue.front().second == time){
                max_heap.push ( queue.front().first );
                queue.pop();
            }

            // STEP 2: if no SCHEDUL-ABLE node in heap (if it cant be scheduled it wont be in heap) --> IDLE --> increment time and next iteration

            if (max_heap.empty()){
                time++;
                continue;
            }

            // STEP 3: pop the top node from heap which can be scheduled --> if it cant be scheduled it wont be in heap

            int task_freq = max_heap.top();
            max_heap.pop();

            // mini: Updates
            time++;
            int new_freq = task_freq - 1;


            // STEP 4: Push it in queue only push if frequency remaining
            if (new_freq > 0) queue.push({new_freq, time + n});

        } 

        return time;
      
    }
};
```
