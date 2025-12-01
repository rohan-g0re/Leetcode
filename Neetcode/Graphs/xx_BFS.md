## BFS --> BREADTH FIRST SEARCH

```cpp

vector <int> BFSonGraph (int V, vector <int> adj[]){

    // 1. initialization of tools

    queue <int> q;
    vector <int> visited (V, 0);
    // vector<vector<int>> adjlist (n+1); --> already provided
    vector<int> result;


    // Step 0: Push root to queue and mark visited
    q.push(0);
    visited[0] = 1;



    while (!q.empty()){

        // 1. pop the front
        int node = q.front();
        q.pop();

        // 2. add in result
        result.push_back(node);

        // 3. Check neighbors in adjanceny list
        for (auto& neighbor : adj[node]){

            // 3.1 if the neighbor is NOT IN QUEUE ( or has never been) then  

            if (visited[neighbor] != 1){
            
                // 3.2 add it in queue and mark visited

                q.push(neighbor);
                visited[neighbor] = 1;
            }
        }
    }


    return result;


}

```

SPACE COMPLEXITY --> 3 x N --> O (N)
TIME COMPLEXITY -->
For every node we traverse all its neighbours --> which is basically the degree of that node --> which is 2 x E (edges)
Hence there total tc is  --> O (N) * 2E
