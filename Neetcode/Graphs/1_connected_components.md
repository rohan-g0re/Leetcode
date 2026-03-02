# Why is this number 16 in neetcode --> we have been doing this since question one

```bash
1. convert edges to adj list
2. recursive dfs code
3. visited driver on rec_dfs

- adj list
- visited vector
```


```cpp

class Solution {

private:
    void rec_dfs(int node, vector<int>& visited, vector<vector<int>>& adjlist){

        // mark visited
        visited[node] = 1;
        
        // find neighbors and traverse unvisited nodes
        for(auto neighbor: adjlist[node]){
            if (visited[neighbor] == 0) rec_dfs(neighbor, visited, adjlist);
        }
        return;
    }

public:
    int countComponents(int n, vector<vector<int>>& edges) {

        // 1. edges to adjacency list 
        vector<vector<int>> adjlist(n);

        for (auto pair: edges ){
            adjlist[pair[0]].push_back(pair[1]);
            adjlist[pair[1]].push_back(pair[0]);
        }

        // 2. visited driver code

        vector<int> visited(n + 1, 0);
        int counter = 0;

        for(int i = 0; i < n; i++){
            if (visited[i] == 0){
                counter++;
                rec_dfs(i, visited, adjlist);
            }
        }

        return counter;

    }
};
```