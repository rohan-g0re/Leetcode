## THE BULLSHIT SIMULATION WAY - DID NOT WORK


###### Intuition 1: starting position is important because it will be the same order in which cars arrive at finsih line/target

###### Intuition 2: only one fleet can reach the target at a given point in time --> which means if at the last instance two cars come together - we dont need to complicate the logic for "how do I call this a fleet on finish line!!!" --> because if the first car just reached target we decrement the number of fleets, in the same way if the second car reached target in the same iteration then it means that "WE ALREADY ACCOUNTED FOR IT AS WE COUNTED THE FIRST CAR AS A FLEET" && basically you are the part of the same fleet now --> basically while pushing: if the distance == target then PUSh && increment number of fleets --> this is to be done by a flag - bcoz if the next car also reaches target then we dont need to increment fleets also dont need to push --> SO swapping from stack to queue is the distance is >= target then dont push

###### INTUITION 3: in every iteration - the first node is the one which reached the target --> so we dont need to check "did we reach target?" for every node --> **DISPROVED** as in a single iteration there can be cars that reach target **BUT ARE NOT PART OF THE SAME FLEET** 



```cpp


class Solution {
public:
    int carFleet(int target, vector<int>& position, vector<int>& speed) {

        // Phase 1. push sorted pairs in queue

        // 1.1 make pairs in vector && sort
        vector<pair<int, int>> pair_vector;

        for(int i = 0; i < position.size(); i++){
            pair_vector.push_back({position[i], speed[i]});
        }

        sort(pair_vector.rbegin(), pair_vector.rend());

        // 1.2 create queue and push pairs in it
        queue<pair<int, int>> q;
        
        for(auto& p : pair_vector){
            q.push(p);
        }


        // PHASE 2 - the main thing
        stack<pair<int, int>> st;
        int fleet = 0;

        while(!q.empty()){
            
            int queue_size = q.size();
            
            for(int i = 0; i < queue_size; i++){

                // 1. take from queue and update
                
                int car_posi = q.front().first;
                int car_speed = q.front().second;
                q.pop();
                car_posi += car_speed; // the iteration

                

                // 2. filling stack based on positions
                
                     // stack not empty
                    
                    // case 1: merge fleet --> continue
                    
                    if (car_posi >= st.top().first){
                        fleet++;
                        continue; // take next node from queue
                    }
                    
                    //Case 2: car is behind --> push 
                    else{     

                        // it can STILL independently reach the target by not being a part of the fleet that already crossed target
                        if(car_posi >= target){
                            fleet++;
                        }
                        else st.push({car_posi, car_speed});
                    // }

                }
            }

            // 3. pop everthing into temp stack for preserving order --> if node has reached target the dont push

            stack<pair<int, int>> temp;
            while(!st.empty()){
                if(st.top().first < target){
                    temp.push(st.top());
                }
                st.pop();
                // we dont push if its already reached target
            }

            // 4. push everything in queue

            while(!temp.empty()){
                q.push(temp.top());
                temp.pop();
            }
        }

        return fleet;
        
    }
};


```


## ACTUAL APPROACH --> calculating total time taken and pushing into stack - if it is less than the already-pushed --> it means that the cars will collide and hence it is basically a fleet  

### **IMPORTANT --> we need to use FLOAT as the time needs to be in decimals**

```cpp

class Solution {
public:
    int carFleet(int target, vector<int>& position, vector<int>& speed) {
        
        vector<pair<int, int>> pairs;

        for(int i = 0; i < position.size(); i++){
            pairs.push_back({position[i], speed[i]});
        }

        // sort in reverse

        sort(pairs.rbegin(), pairs.rend());


        stack<double> st;  //stores times

        for(auto& pair: pairs){
            double distance = (target - pair.first);
            double time = distance / pair.second;

            if(st.empty() || time > st.top()){
                st.push(time);
            }
            // else it means that it got merged into a fleet 
        }
        return st.size();      
    }
};


```