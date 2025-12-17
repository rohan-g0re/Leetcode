# The complete intuition is that we need to carry parent along with a BFS traversal. If any time a neighbor is visited and is not the parent that it came from, then it means that we have found a cycle. That's it!

```cpp

class Solution {
public:
    bool validTree(int n, vector<vector<int>>& edges) {


        vector<vector<int>> adj_list (n);

        for (auto pair : edges){
            adj_list [ pair[0] ] .push_back(pair[1]);
            adj_list [ pair[1] ] .push_back(pair[0]);
        }

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