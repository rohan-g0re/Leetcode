
# INTUITIONS:
1. it is a disconnected graph with COMPONENTS 
2. Whichver traversal I use I would need to restart it, when it reaches end --OR-- i need to start it from ever NON-VISITED point
3. need a visited array

> CHALLENGE --> working with adjacency matrix


```cpp
class Solution {
public:

    // void bfs()

    int findCircleNum(vector<vector<int>>& isConnected) {

        int n = isConnected.size();

        vector <int> visited (n, 0);
        int provinces = 0;
        
        for (int i = 0; i < n; i++){

            if (visited[i] != 1){

                provinces++;

                queue <int> q;

                q.push(i);

                while (!q.empty()){
                    int node = q.front();
                    q.pop();


                    // find neighbors
                    for (int col = 0; col < n; col++){

                            // is neighbor                  not visited
                        if (isConnected[node][col] == 1 && visited[col] != 1){

                            q.push(col);
                            visited[col] = 1;
                        }
                    }
                }
            }

        }

        return provinces;
       
    }
};

```

#### SC 
- visited array O (n)
- resursion stack **if dfs used** O(n)


#### TC --> O (V + 2E) which is the basic BFS TC