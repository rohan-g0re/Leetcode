## DFS --> DEPTH FIRST SEARCH (iterative)

```cpp

vector <int> DFSonGraph (int V, vector <int> adj[]){

    // 1. initialization of tools

    stack <int> stack;
    vector <int> visited (V, 0);
    // vector<vector<int>> adjlist (n+1); --> already provided
    vector<int> result;


    // Step 0: Push root in stack and mark visited
    stack.push(0);
    visited[0] = 1;



    while (!stack.empty()){

        // 1. pop the top
        int node = stack.top();
        stack.pop();

        // 2. add in result vector
        result.push_back(node);

        // 3. Check neighbors in adjacency list
        for (auto& neighbor : adj[node]){

            // 3.1 if the neighbor is NOT IN STACK ( or has never been) then  

            if (visited[neighbor] != 1){
              
                // 3.2 add it in stack and mark visited

                stack.push(neighbor);
                visited[neighbor] = 1;
            }
        }
    }

    return result;


}

```

## DFS --> DEPTH FIRST SEARCH (recursive)

```cpp

void DFS_Recursive (int node, vector<int>& adj[], vector <int>& visited, vector <int>& result){

    // 1. mark in visited
    visited[node] = 1;

    // 2. Add in result
    result.push_back(node);


    // 3. Check all the neighbors... 

    for (auto& neighbor : adj[node]){

        // and if any of them is not visited ....
        if (visited[neighbor] != 1){

            // 3.1 RECURSE ON THEM
            DFS_Recursive(neighbor, adj, visited, result);

        }

    }
}

vector <int> DFSonGraph (int V, vector <int> adj[]){

    vector<int> visited (V, 0);
    vector<int> result;

    DFS_Recursive(0, adj, visited, result);

    return result;

}

```

TC --> O (V + 2E)