# We are supposed to use TOPOLOGICAL SORTING to detect cycle (problem 1) as well as to return the actual order of courses (problem 2)

```cpp

class Solution {

private:
    vector<int> topo_sort (int numCourses, vector<vector<int>>& prereq){

        // STEP 1: add in indegree array & an adj list

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

        vector<int> result;

        // STEP 3: LOOP BABY

        while (!q.empty()){

            // 3.1 pop a node and add in result
            int node = q.front();
            q.pop();
            result.push_back(node);
            
            // 3.2 check all the outgoing nodes fron the "NODE" and decrement their in-degree values

            for(auto v : adjlist[node]) {
                in_degree[v]--;


                // 3.3 IS THERE ANY in-degree == 0?

                // since we made changes(decrements) to only "NODE"'s destinations -- therefore we can only check if "THEY" have reached zero

                // IMPORTANT --> WE DONT HAVE TO CHECK EVERYTHING

                if(in_degree[v] == 0){
                    q.push(v);
                }

                
            }
        }

        // STEP 4: Check the final sorted order

        if (result.size() == numCourses) return result;
        return {};
    }


public:
    vector<int> findOrder(int numCourses, vector<vector<int>>& prerequisites) {

        return topo_sort(numCourses, prerequisites);
        
    }
};

```