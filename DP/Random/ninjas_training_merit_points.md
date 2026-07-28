# Ninja's Training / Merit Points

## INTUITION
- each day pick **1 of 3 tasks** --> cannot pick same task as **yesterday**
- classic 2D DP --> day + last chosen task

#### WHAT DOES THE DP TABLE MEAN?
- `dp_table[day][last]` = **max points** from day `0..day`, if yesterday's task was `last`
- `last` can be `0,1,2` (actual tasks) **OR** `3` meaning **no restriction** (used as starting state)
- size = `n x 4`

#### HOW DO WE FILL?
1. **Day 0 base** --> for each possible `last`, store max among tasks that are NOT `last`
2. For each later day + each possible `last`:
   - try every `task != last`
   - prospect = `points[day][task] + dp_table[day-1][task]`
   - keep the max
3. Answer = `dp_table[n-1][3]` --> no restriction on last day

```cpp
int ninjatraining(int n, vector<vector<int>>& points){

    // dp[day][last] --> max points till this day, given last chosen task
    vector<vector<int>> dp_table (n, vector<int>(4, 0));

    // base --> day 0
    // if last was X, we could only have chosen something else on day 0
    dp_table[0][0] = max(points[0][1], points[0][2]);
    dp_table[0][1] = max(points[0][0], points[0][2]);
    dp_table[0][2] = max(points[0][0], points[0][1]);
    dp_table[0][3] = max(points[0][0], max(points[0][1], points[0][2]));

    // for every day
    for (int day = 1; day < n; day++){

        // for every possible last chosen
        for (int last = 0; last < 4; last++){

            dp_table[day][last] = 0;

            // try every task that is NOT last
            for (int task = 0; task < 3; task++){

                if (task != last){
                    // take this task today + best till yesterday ending with this task
                    int current_prospect = points[day][task] + dp_table[day - 1][task];
                    dp_table[day][last] = max(dp_table[day][last], current_prospect);
                }
            }
        }
    }

    // last = 3 --> no restriction on final day
    return dp_table[n - 1][3];
}
```
