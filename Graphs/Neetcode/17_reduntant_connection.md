

## Failed Approach --> I was trying to use DFS to find out the cycle and return the exact edge where we got the cycle --> but this edge is **NOT NECESSARILY the LAST EDGE THAT WAS ADDED**

### My CODE: it would pass logic and give correct edge BUT NOT THE LAST ADDED EDGE

```cpp
class Solution {

vector<int> rec_dfs(vector<vector<int>>& adjlist, vector<int>& visited, int parent, int current){

    // mark visited
    visited[current] = 1;

    // find neighbors

    for(auto neighbor : adjlist[current]){
        // VALID: not visited
        if(visited[neighbor] != 1){
            vector<int> result = rec_dfs(adjlist, visited, current, neighbor);
            if (!result.empty()) return result;
        }

        // INVALID: Visited and NOT parent
        else if(neighbor != parent){
            return {neighbor, current};
        }
    }

    return {};
}

public:
    vector<int> findRedundantConnection(vector<vector<int>>& edges) {

        // 1. create adjlist

        int n = edges.size(); //given in constraints
        vector<vector<int>> adjlist(n + 1);

        for (auto edge : edges){
            adjlist[edge[0]].push_back(edge[1]);
            adjlist[edge[1]].push_back(edge[0]);
        }

        // 2. DFS for cycle detection

        // visited array to keep track of nodes only --> hence 1D
        vector<int> visited(n + 1, 0);


        return rec_dfs(adjlist, visited, -1, 1);

        
    }
};
```


## ACTUAL SOLUTION --> UNION FIND