/*

INTUITIONS:
1. the tasks with more frequency should be executed first 


## BRUTE
1. maintain a max heap such that the alphabet with most amount of tasks remaining is at top

2. Pick that task - decrement its remaning tasks

3. update the colldown in a map with n 

--- 
4. next iteration: 
    - we traverse the map to decrement everybody's cooldown by 1, bcoz 1 CPU cycle passed 
    

IMP CASE:
1. if task at heap.top has more time left in cooling down - WHAT TO DO;

: take a vector and pop all of them until we find the one who can be scheduled --> if not found then idle


-------


## BETTER 
- keep a map such that <task, <remaining_count, cooldown> >

- at each iteration we decrement cooldown and pick the one who has 0 cooldown after decreament and decreament thier rem_count

- if no such task - idle

TOOOOOOOO MANY CASES 


# ACTUAL SOLUTION --> Using Max Heap and a Queue 

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

            // STEP 3: pop the top node from heap which can be scheduled --> if it cant be scheduled it won be in heap

            int task_freq = max_heap.top();
            max_heap.pop();

            // STEP 3.mini: Updates
            time++;
            int new_freq = task_freq - 1;


            // STEP 4: Push it in queue only push if frequency remaining
            if (new_freq > 0) queue.push({new_freq, time + n});

        } 

        return time;
        
    }
};

```