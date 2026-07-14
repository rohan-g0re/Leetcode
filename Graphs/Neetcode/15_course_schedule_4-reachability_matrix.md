## Failed Approach
1. I started by using topo sort and thought that, for every query I only need to check if index of u is before index of v in topologically sorted array.
2. But then I understood that the question is not just about order but the nodes should be directly or indirectly connected.
3. Example Graph: a->c, b -> c; Query: [a, b] --> in this case the topo order will be `a b c` --> but this does not mean that `a` is a pre-req of `b` **because there is no edge / path that connects them**.
##### 4. Therefore, we don't need topological order; we need a reachability matrix. When looking at the constraints, we also saw that our graph will not have any cycles. Hence, this makes it way easier.


Therrefore we can do it without topo order I guess.

### Approach 1: BRUTE: For every query [u, v], DFS from u and check if v is found


## Approach 2: Complete a DFS from every node and maintain a visited-like array called Reachability Matrix.

```cpp
class Solution {

private:

    void rec_dfs(vector<vector<int>>& adjlist, vector<vector<int>>& reach, int source, int node){

        // find neighbors

        for(auto neighbor : adjlist[node]){
            // traverse if NOT visited
            if (reach[source][neighbor] != 1){
                
                // mark visited from source but traverse on the next neighbor
                
                reach[source][neighbor] = 1;
                rec_dfs(adjlist, reach, source, neighbor);
            }
        }

    }


public:
    vector<bool> checkIfPrerequisite(int numCourses, vector<vector<int>>& prerequisites, vector<vector<int>>& queries) {

        if (prerequisites.size() == 0){
            return vector<bool> (numCourses, false);
        }


        // 1. create adjlist

        vector<vector<int>> adjlist(numCourses); // a --> b
        for(auto req : prerequisites){
            adjlist[req[0]].push_back(req[1]);
        }


        // 2. dfs on adj list

        vector<vector<int>> reach (numCourses, vector<int>(numCourses, 0));

        // the driver is based upon the question that -- the name of courses are basically from 0 to numcourses-1

        for (int i = 0; i < numCourses; i++){
            rec_dfs(adjlist, reach, i, i);
        }



        // 3. check matrix for answers

        vector<bool> result;

        for(auto pair : queries){
            if (reach[ pair[0] ][ pair[1] ] == 1) result.push_back(true);
            else result.push_back(false);
        }

        return result;
    }
};

```

##### EXTRA --> instead of matrix you can also use `map<int, unordered_set<int>>`