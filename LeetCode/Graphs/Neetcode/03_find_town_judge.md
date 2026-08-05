## Inutuition
1. indegree should be n-1 
2. outdegree should be 0

##### can do this in a complicated way using adjacency lists or simply by keeping 2 arrays for frequencies

## 2 arrays
```cpp
class Solution {
public:
    int findJudge(int n, vector<vector<int>>& trust) {
        
        // doing n+1 to remove zero based indexing
        vector<int> in_degree (n + 1, 0); 
        vector<int> out_degree (n + 1, 0);   

        for (auto pair : trust){
            out_degree[pair[0]]++;
            in_degree[pair[1]]++;
        }

        for (int i = 1; i < n+1; i++){
            if (in_degree[i] == n-1 && out_degree[i] == 0) return i;
        }
        
        return -1;
    }
};

```

## 1 array --> using in_degree - out_degree

```cpp
class Solution {
public:
    int findJudge(int n, vector<vector<int>>& trust) {
        
        // doing n+1 to remove zero based indexing
        vector<int> optimal (n + 1, 0); 
        
        for (auto pair : trust){
            optimal[pair[1]]++; // Represents the in_degree being added
            optimal[pair[0]]--; // Represents the out_degree being subtracted
        }

        for (int i = 1; i < n+1; i++){
            if (optimal[i] == n-1) return i;
        }
        
        return -1;
    }
};

```