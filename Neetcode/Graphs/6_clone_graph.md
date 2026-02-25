## INTUITION:

- We need to deep-copy every node, but a node can appear as a neighbor of multiple other nodes — so we can't just blindly create a new node every time we see it
- Use a hashmap (`old node → cloned node`) to track which nodes we've already cloned
- DFS through the graph: for each node, create its clone, store it in the map, then recursively clone all its neighbors
- If we encounter a node that's already in the map, just return the existing clone instead of creating a duplicate — this also prevents infinite loops in cyclic graphs
- After recursing on all neighbors, push their cloned pointers into the current clone's neighbor list

#### IMPORTANT --> we will need a map to keep a track of nodes that we have created --> as a given node can have multiple edges, therefore it will be referenced as a "neighbor" multiple times --> so everytime we are not supposed to create a new node BUT join the edge to the already created unique node 



```cpp
// Definition for a Node.
class Node {
public:
    int val;
    vector<Node*> neighbors;
    Node() {
        val = 0;
        neighbors = vector<Node*>();
    }
    Node(int _val) {
        val = _val;
        neighbors = vector<Node*>();
    }
    Node(int _val, vector<Node*> _neighbors) {
        val = _val;
        neighbors = _neighbors;
    }
};
```


## CODE:

```cpp
class Solution {
private:

    unordered_map<Node*, Node*> visited;
    // key: actual node <----> value: cloned node that we created 

public:
    Node* cloneGraph(Node* node) {

        // 1. BASE CASES

        // 1.1 reached leaf node 
        if (node == nullptr) return nullptr;

        // 1.2 node already created
        if (visited.find(node) != visited.end())return visited[node];

        
        // 2. RECURSION LOGIC


        Node* clone = new Node (node->val);
        // CLONING VALUE: we create a BRAND NEW node with the same value as the one to be cloned 
        
        // But still the neighbor list is remaining --> we do that by going in depth and creating that node first and then it will get added to this node's neighbor list

        visited[node] = clone;

        // CLONING NEIGHBOR
        for (auto neighbor : node -> neighbors){
            
            clone->neighbors.push_back(cloneGraph(neighbor));

        }

        return clone;
        
    }
};