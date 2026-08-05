

```cpp

class Solution {

private:
    bool topo_sort (int numCourses, vector<vector<int>>& prereq){

        // STEP 1: BUILD indegree array & adjacency list

        vector<vector<int>> adjlist (numCourses);
        vector<int> in_degree(numCourses, 0);

        for(auto& pair : prereq){
            in_degree [ pair[0] ]++;
            adjlist[pair[1]].push_back(pair[0]);
        }



        // STEP 2: push all indegree = 0 nodes into queue

        queue <int> q;
        for (int i = 0; i < numCourses; i++){
            if (in_degree[i] == 0){
                q.push(i);
            }
        }

        // MAIN LOGIC ----->>>>>> CAN USE A VECTOR IF WE WANT TO STORE THE SORTED ORDER
        int counter = 0; 

        // STEP 3: LOOP BABY

        while (!q.empty()){

            // 3.1 pop a node and add in result counter
            int node = q.front();
            q.pop();
            counter++;
            
            // 3.2 check all the outgoing nodes fron the "NODE" and decrement their in-degree values

            for(auto v : adjlist[node]) {
                in_degree[v]--;


                // 3.3 IS THERE ANY in-degree == 0?
                if(in_degree[v] == 0){
                    q.push(v);
                }
            }
        }

        // STEP 4: Check the final sorted order

        if (counter == numCourses) return true;
        return false;
    }

public:
    bool canFinish(int numCourses, vector<vector<int>>& prerequisites) {
        return topo_sort(numCourses, prerequisites);
    }
};

```