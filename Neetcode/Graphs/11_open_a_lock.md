## INTUITION:


1. we start BFS from 0000
2. we have 8 possible moves: + and - for each of the 4 digits
3. IMP: we have 2 options to keep a track of STEPS:
        1. use snapshotting
        2. store as pair with number
4. IMP: we check every neighbor to be one of the 2 things:
        1. either a valid node to be traversed to (in a decision tree)
        2. target --> if target then return snapshot_time + 1;


5. **MATURE THOUGHTS: we can add +1 to 0000 --> 0001 and  push --> BUT we can again do -1 and push 0000 --> therefore we will be in infinite cycle --> THERFORE KEEP A CYCLE OF VISITED NODES**




# Solution 1: Using for loop for checking if neighbor is deadend --> TLE

```cpp
class Solution {

private:

    bool check_deadend(string number, vector<string>& deadends){

        for (string deadend : deadends){
            if (number == deadend) return false; // invalid neighbor;
        }
        return true; // valid neighbor

    }

public:
    int openLock(vector<string>& deadends, string target) {

        for (string deadend : deadends){
            if (deadend == "0000") return -1;
        }
        
        unordered_set<string>visited;
        queue <string> q;
        visited.insert("0000");
        q.push("0000");

        int snapshot = 0;


        while (!q.empty()){


            snapshot++;
            int qsize = q.size();

            for (int ele = 0; ele < qsize; ele++){

                string node = q.front();
                q.pop();


                // check neighbor

                for(int i = 0; i < 4; i++){
                    // neighbor digit change calculation
                    
                    // step 1: INT: get digit
                    int digit = node[i] - '0';

                    // step 2: INT: calculate new digit
                    int new_digit_add = (digit + 1) % 10;
                    int new_digit_sub = (digit - 1 + 10) % 10;

                    // step 3: STR: calculate neigbors with new digit
                    string new_string_add = node;
                    string new_string_sub = node;
                    new_string_add[i] = '0' + new_digit_add;
                    new_string_sub[i] = '0' + new_digit_sub;

                    // step 4: STR: check if new number after replacing == target or not
                    if (new_string_add == target || new_string_sub == target) return snapshot;

                    // step 5: STR: check valid neighbor or not

                    if (check_deadend(new_string_add, deadends) && !visited.count(new_string_add)){
                        visited.insert(new_string_add);
                        q.push(new_string_add);
                    }
                    if (check_deadend(new_string_sub, deadends)  && !visited.count(new_string_sub)){
                        visited.insert(new_string_sub);
                        q.push(new_string_sub);
                    }
                }
            }
        }
        return -1;
    }
};
```




# Solution 2: No for loop - USING SET for quick lookup

```cpp

class Solution {

public:
    int openLock(vector<string>& deadends, string target) {

        unordered_set<string>visited;
        unordered_set<string>dead (deadends.begin(), deadends.end());

        if (dead.count("0000")) return -1;
        if (target == "0000") return 0;


        queue <string> q;
        visited.insert("0000");
        q.push("0000");

        int snapshot = 0;


        while (!q.empty()){


            snapshot++;
            int qsize = q.size();

            for (int ele = 0; ele < qsize; ele++){

                string node = q.front();
                q.pop();


                // check neighbor

                for(int i = 0; i < 4; i++){
                    // neighbor digit change calculation
                    
                    // step 1: INT: get digit
                    int digit = node[i] - '0';

                    // step 2: INT: calculate new digit
                    int new_digit_add = (digit + 1) % 10;
                    int new_digit_sub = (digit - 1 + 10) % 10;

                    // step 3: STR: calculate neigbors with new digit
                    string new_string_add = node;
                    string new_string_sub = node;
                    new_string_add[i] = '0' + new_digit_add;
                    new_string_sub[i] = '0' + new_digit_sub;

                    // step 4: STR: check if new number after replacing == target or not
                    if (new_string_add == target || new_string_sub == target) return snapshot;

                    // step 5: STR: check valid neighbor or not

                    if (!dead.count(new_string_add) && !visited.count(new_string_add)){
                        visited.insert(new_string_add);
                        q.push(new_string_add);
                    }
                    if (!dead.count(new_string_sub)  && !visited.count(new_string_sub)){
                        visited.insert(new_string_sub);
                        q.push(new_string_sub);
                    }
                }
            }
        }
        return -1;
    }
};
```

# Things to learn:
#### 1. To convert an integer digit to a character: `'0' + digit;`  // Yes, this gives you the char representation of a digit.
#### 2. To convert a character digit to an integer: `char_digit - '0';`  // Yes, this converts a char like '3' to int 3.