/*
 * 1376. Time Needed to Inform All Employees  (Medium)
 * Tags: Tree, DFS, BFS
 *
 * PROBLEM
 * -------
 * A company has n employees with IDs 0..n-1. One of them is the head,
 * with ID headID.
 *
 * manager[i] is the direct manager of employee i. The head has
 * manager[headID] = -1. The reporting relationships form a tree.
 *
 * The head wants to share urgent news with everyone. The news spreads
 * down the hierarchy: each employee tells their direct subordinates,
 * who then tell their own direct subordinates, and so on.
 *
 * informTime[i] is the number of minutes employee i needs to inform
 * all of their direct subordinates. Once those minutes pass, every
 * direct subordinate of i can begin spreading the news further.
 *
 * Return the number of minutes until every employee has the news.
 *
 * EXAMPLE 1
 *   Input:  n = 1, headID = 0, manager = [-1], informTime = [0]
 *   Output: 0
 *   Why:    The head is the only employee.
 *
 * EXAMPLE 2
 *   Input:  n = 6, headID = 2, manager = [2,2,-1,2,2,2],
 *           informTime = [0,0,1,0,0,0]
 *   Output: 1
 *   Why:    Employee 2 manages everyone else and needs 1 minute
 *           to tell all of them at once.
 *
 * EXAMPLE 3
 *   Input:  n = 6, headID = 2, manager = [2,2,-1,2,3,3],
 *           informTime = [0,0,3,2,0,0]
 *   Output: 5
 *   Why:    2 -> {0,1,3} takes 3 min, then 3 -> {4,5} takes 2 more.
 *
 * CONSTRAINTS
 *   1 <= n <= 10^5
 *   0 <= headID < n
 *   manager.length == n
 *   0 <= manager[i] < n, except manager[headID] == -1
 *   informTime.length == n
 *   0 <= informTime[i] <= 1000
 *   informTime[i] == 0 if employee i has no subordinates
 *   Every employee is guaranteed to be reachable from the head.
 */

 #include <bits/stdc++.h>
 using namespace std;


/*
 
INTUITION:
3 ways of represneting the tree (examples wrt eg3 from above):
1. placing nodes in tree format --> nodes represent which index is their manager --> the already given format
2. nodes as index of manager [2, [0,1,3], [_,_,_,_,4,5]]
3. nodes represent cost [3, [0,0,2], [_,_,_,_,0,0]]

INTUITION 1 --> type 3 is the best --> we will just need to make a simple dfs traversal to get the total time

CHALLENGE 1 --> how to build this tree

INTUITION 2 --> manager is the tree in upward direction - from leaf to root
- hence we can brute force on the array for every path
- just start and keep adding time to inform until the manager is ceo



*/

// Input:  n = 6,
// headID = 2,
// manager = [2,2,-1,2,3,3],
// informTime = [0,0,3,2,0,0]


 

## Approach 1 - Brute --> trace every path from leaf to ceo --> n2 time complexity

```cpp
 class Solution {
 public:
     int numOfMinutes(int n, int headID, vector<int>& manager, vector<int>& informTime) {

        int maxi = INT_MIN;

        for (int i = 0; i < n; i++){
 
            // base case already ceo
            if (i == headID) continue;

            // process it using while loop until the node has "-1"
            int index = i;
            int time = 0;


            // loop until reach ceo
            while(index != -1){

                // add time at current level
                time += informTime[index];
                maxi = max(maxi, time); // update the max time if it is

                // go to parent index
                index = manager[index];
            }
        }

        return maxi;
        
     }
 };
 ```


## Approach 2 - Better

```cpp


 class Solution {
 public:
     int numOfMinutes(int n, int headID, vector<int>& manager, vector<int>& informTime) {
        
     }
 };


 int main() {
     Solution sol;
 
     vector<int> m1 = {-1};
     vector<int> t1 = {0};
     cout << sol.numOfMinutes(1, 0, m1, t1) << "  (expected 0)" << endl;
 
     vector<int> m2 = {2, 2, -1, 2, 2, 2};
     vector<int> t2 = {0, 0, 1, 0, 0, 0};
     cout << sol.numOfMinutes(6, 2, m2, t2) << "  (expected 1)" << endl;
 
     vector<int> m3 = {2, 2, -1, 2, 3, 3};
     vector<int> t3 = {0, 0, 3, 2, 0, 0};
     cout << sol.numOfMinutes(6, 2, m3, t3) << "  (expected 5)" << endl;
 
     return 0;
 }

 ```