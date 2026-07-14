# 1. Detect cycle in undirected graph using BFS

### The complete intuition is that we need to carry PARENT along with a BFS traversal.

### If anytime a neighbor is VISITED & is NOT THE PARENT that it came from, then it means that we have found a cycle. That's it!

```cpp

class Solution {
public:
    bool validTree(int n, vector<vector<int>>& edges) {

      
        // We need an adjacency list or an adjacency matrix for this, so that is why we create it!
        vector<vector<int>> adj_list (n);

        for (auto pair : edges){
            adj_list [ pair[0] ] .push_back(pair[1]);
            adj_list [ pair[1] ] .push_back(pair[0]);
        }


// --------------> CYCLE DETECTION LOGIC


        vector<int> visited (n, 0);
        queue<pair<int, int>> q;

        q.push({0, -1});
        visited[0] = 1;

        while (!q.empty()){
          
            // 1. pop front
            int node = q.front().first;
            int parent = q.front().second;
            q.pop();

            // 2. check for neighbors 
            for (auto neighbor : adj_list[node]){

                // 2.1. Oh my god, the neighbor is visited. 
                if (visited[neighbor] == 1){

                    // 2.1.1 If the visited guy is not the parent, then it's done. It's a cycle. 
                    if (neighbor != parent) return false;
                  
                    // 2.1.2. If it's visited and it's not 2.1.1, then it is basically a parent, so don't do anything else, continue to the next neighbor. 
                    continue;

                }

// --------------> CYCLE DETECTION LOGIC



                // 2.2. not visited

                visited [ neighbor ] = 1;
                q.push({neighbor, node});

            }
        }



        // IMPORTANT CASE 2 - if the graph is disconnected, then it's not a valid tree. So, check if everyone is visited. 

        for (auto num: visited){
            if (num == 0) return false;
        }

        return true;
    }
};

```

#### Complexities

- Time complexity O(n + 2e)
- Space complexity O(n).

# 2. Detect cycle in undirected graph using DFS

### The complete intuition is that we need to carry PARENT along with a recursive DFS traversal.

### If anytime a neighbor is VISITED & is NOT THE PARENT that it came from, then it means that we have found a cycle.

```cpp

class Solution {

private:

    bool dfs_rec(vector<vector<int>>& adj_list, vector<int>& visited, int parent, int current){

        visited[current] = 1;

        // check neighbors

        for(int neighbor: adj_list[current]){
          
            // 1. Non visited
            if (visited[neighbor] != 1){
                dfs_rec (adj_list, visited, current, neighbor);
            }

            // visited --> can be parent || can be cycle
            else if(visited[neighbor] == 1 && neighbor != parent){
                return false;
            }
        }

        return true;
    }

public:
    bool validTree(int n, vector<vector<int>>& edges) {
  
        // We need an adjacency list or an adjacency matrix for this, so that is why we create it!
        vector<vector<int>> adj_list (n);

        for (auto pair : edges){
            adj_list [ pair[0] ] .push_back(pair[1]);
            adj_list [ pair[1] ] .push_back(pair[0]);
        }


// --------------> CYCLE DETECTION LOGIC
        vector<int> visited (n, 0);

        visited[0] = 1;
        if (!dfs_rec(adj_list, visited, -1, 0)) return false;

// --------------> CYCLE DETECTION LOGIC



        // IMPORTANT CASE 2 - if the graph is disconnected, then it's not a valid tree. So, check if everyone is visited. 

        for (auto num: visited){
            if (num == 0) return false;
        }

        return true;
    }
};

```

#### Complexities

- Time complexity O(n + 2e)
- Space complexity O(n).
