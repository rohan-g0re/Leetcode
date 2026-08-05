## INTUITION:

1. disconnected graph with COMPONENTS --> same as provinces / islands
2. whichever traversal I use --> restart when it ends --> start from every NON-VISITED node
3. need visited array
4. edges given as list --> build adj list first

```cpp
class Solution {

private:

    void dfs(vector<vector<int>>& adj, vector<int>& visited, int node) {

        visited[node] = 1;

        // explore neighbors
        for (int neighbor : adj[node]) {
            if (visited[neighbor] != 1) {
                dfs(adj, visited, neighbor);
            }
        }

        return;
    }

public:
    int countComponents(int n, vector<vector<int>>& edges) {

        // build adj list
        vector<vector<int>> adj(n);

        for (auto& e : edges) {
            adj[e[0]].push_back(e[1]);
            adj[e[1]].push_back(e[0]);
        }

        vector<int> visited(n, 0);
        int components = 0;

        for (int i = 0; i < n; i++) {

            // if un-visited --> explore
            if (visited[i] == 0){
                components++;
                dfs(adj, visited, i);
            }
        }

        return components;
    }
};
```
