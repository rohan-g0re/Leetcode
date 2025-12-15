```cpp


int ninjatraining(int n, vector<vector<int>>& points){

    vector<vector<int>> dp_table (n, vector<int>(4, 0));

    // base cases initialized for day 0 --> which are basically MAX after a task is chosen

    dp_table[0][1] = max (points[0][0], points[0][2];
    dp_table[0][2] = max (points[0][0], points[0][1];
    dp_table[0][3] = max (points[0][0], max (points[0][1], points[0][2];)
    dp_table[0][0] = max (points[0][1], points[0][2];

    // for every day .....
    for (int day = 1; day < n; day++){

        // if we had chosen "task x" for previous day .....
        for (int last_chosen = 0; last_chosen < 4; last_chosen++){

            dp_table[day][last_chosen] = 0;


            // what is the max that we can get for this current day + the best of that task for previous day
            for(int task = 0; task < 3; task++){

                if (task != last_chosen){
                    int current_prospect =  points[day][task] + dp_table[day-1][task];
                    dp[day][last] = max (dp[day][last], current_prospect);
                }

            }

        }

    }

}

```