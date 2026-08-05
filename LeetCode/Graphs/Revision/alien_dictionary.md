# Approach 1 - Topological Sort, Traversal && Cycle detection using Kahn's algorithm

MAIN LOGIC --> our in_degree values:
- -1 : by default - means that alphabet not present in words
- 0 : alphabet in words
- more than 0 : incoming edges



### Code:

```cpp
class Solution {

private:


    string topo_sort(vector<vector<int>>& adjlist, vector<int>& in_degree){
        
        // step 2: Push All nodes with in_degree = 0 into queue

        queue<int> q;
        for(int i = 0; i < in_degree.size(); i++){
            if(in_degree[i] == 0)q.push(i);
        }

        vector<int> result;

        // STEP 3: Loop baby
        while(!q.empty()){
            
            // 3.1 pop and add to result
            int node = q.front();
            q.pop();
            result.push_back(node);

            // 3.2 check all neighbors / outgoing edges

            for(auto v : adjlist[node]){
                
                // 3.3 decrement indegree 
                in_degree[v]--;

                // 3.4 if indegree becomes zero then push to queue
                if(in_degree[v] == 0) q.push(v);
            }
        }

        // NEXT STEPS: 
        // verify if cycle: if indegree has more than 0 --> CYCLE PRESENT

        for(auto degree : in_degree){
            if(degree > 0) return "";
        }

        // NO CYCLE --> structure string
        string res = "";
        for(auto i : result){
            res.push_back(i + 'a');
        }
        return res;
    }


public:
    string foreignDictionary(vector<string>& words) {

        // adjacency list

        vector<vector<int>> adjlist (26);
        vector<int> in_degree(26, -1);


        // mark all PRESENT LETTERS as zero - ABSENT LETTERS will stay '-1'
        for(auto word : words){
            for(auto c : word){
                if(in_degree[c - 'a'] == -1) in_degree[c - 'a'] = 0; // no matter how many time they occur - their in degree is ZERO
            }
        }


        // loop to compare pairs of words

        for(int i = 0; i < words.size() - 1; i++){
            
            string s1 = words[i];
            string s2 = words[i + 1];

            // set a pointer --> when in-equality found --> add to adjacency list
            int p = 0;
            bool found = false;

            while(p < s1.size() && p < s2.size()){

                // non match --> create an edge such that letter in s1 comes BEFORE letter in s2

                if(s1[p] != s2[p]){
                    int u = s1[p] - 'a';
                    int v = s2[p] - 'a';

                    // update adjlist and in-degree array
                    adjlist[u].push_back(v);
                    in_degree[v]++;

                    found = true;
                    break;
                }

                // match --> move ahead
                else p++;
            }
            /*
            if found STILL equal to False:
                1. both words were same
                2. first word was longer than second and had the same string --> abc, ab --> this is INVALID
            */
            if(found == false && s1.size() > s2.size()){
                return ""; // return empty string - since the question is flawed the
            }

        }



        // now we need to perform topological sort on this adjacency list

        return topo_sort(adjlist, in_degree);


    }
};
```



# Approach 2 - Topological sort, traversal, and cycle detection using DFS.


MAIN LOGIC --> our visited array right now only marks those letters of alphabet which are in the problem  - visited array values:
- -1 : by default - means that alphabet not in words
- 0 : alphabet in words
- 1 : current_path_visited (during dfs)
- 2: done (during dfs)


### Code:


```cpp
class Solution {

private:

    bool dfs(vector<vector<int>>& adjlist, vector<int>& visited, int node, stack<int>& st){

        // 1. mark node visited
        visited[node] = 1;

        // 2. find neighbors

        for(auto v : adjlist[node]){

            if(visited[v] == 1) return false; // path visited - hence cycle;


            /*
            CRAZY STUFF - 1 stone - 2 pigeons
            - what we want to achieve:
                1. we want to account for the case where we handle a recursive call returning false - as we would like to terminate it then
                2. also we want to do steps after the for loop if "no cycle" --> step 3.

            HENCE WE WRITE THIS IF CASE --> by writing dfs(...) == false:
                1. WE EXECUTE THE DFS 
                2. terminate this complete call - if got false from child call
                3. continue THIS CALL - If got true from child call
            */



            if(visited[v] == 0 && dfs(adjlist, visited, v, st) == false) return false;
            
        }

        // 3. this node is done --> mark done --> push in stack --> return
        visited[node] = 2;
        st.push(node);
        return true;
    }

    string topo_sort(vector<vector<int>>& adjlist, vector<int>& visited){

        stack<int> st;

        // 1. component driver

        for(int i = 0; i < visited.size(); i++){
            if(visited[i] == 0){
                if(dfs(adjlist, visited, i, st) == false) return ""; // 'i' tells us the letter
            }
        }

        // 2. pop elements and push_back toa string to give final result
        string result = "";
        while(!st.empty()){
            char letter = st.top() + 'a';
            result.push_back(letter);
            st.pop();
        }

        return result;

    }


public:
    string foreignDictionary(vector<string>& words) {


        // adjacency list

        vector<vector<int>> adjlist (26);
        vector<int> visited(26, -1);



        // loop to compare pairs of words

        for(int i = 0; i < words.size() - 1; i++){
            
            string s1 = words[i];
            string s2 = words[i + 1];

            // set a pointer --> when in-equality found --> add to adjacency list
            int p = 0;
            bool found = false;

            while(p < s1.size() && p < s2.size()){
                /*
                non match --> create an edge such that letter in s1 comes BEFORE letter in s2
                
                */
                if(s1[p] != s2[p]){
                    int u = s1[p] - 'a';
                    int v = s2[p] - 'a';
                    adjlist[u].push_back(v);
                    found = true;
                    break;
                }

                // match --> move ahead
                else p++;
            }
            /*
            if found STILL equal to False:
                1. both words were same
                2. first word was longer than second and had the same string --> abc, ab --> this is INVALID
            */
            if(found == false && s1.size() > s2.size()){
                return ""; // return empty string - since the question is flawed the
            }

        }


        for(auto word : words){
            for(auto c : word){
                if(visited[c - 'a'] == -1) visited[c - 'a'] = 0;
            }
        }


        // now we need to perform topological sort on this adjacency list

        return topo_sort(adjlist, visited);


    }
};

```