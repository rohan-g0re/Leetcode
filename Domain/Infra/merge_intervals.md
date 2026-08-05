# LC 56 - Medium

## INTUITION

- maybe needs sorting every pair and then traverse --> as sorting would sort all the pairs inside our list as well 

# Approach 1 - Better
- we basically have 3 ways that an interval can get processed as
    1. it completely fits in the last result interval --> in this case, we have already represented it -> so continue to next interval
    2. its overlapping i.e. its starting is in the last range but ending is more than last one --> in this case we need to merge it by keeping the starting same (of last result interval) and choosing the greater ending 
    3. no overlap

### Algo

```bash

1. Sort 

2. For loop of i --> 
 
    2.1 initalize start = intervals[i][0] and end = intervals[i][1]

    2.2 **Can we accomodate this pair in the last pair pushed in answer array** 
        - yes: continue --> move to next i 

    2.3 if no --> this (start, end) is going to be the new pair --> So before adding this, lets find if any of the NEXT PAIRS CAN BE MERGED INTO THIS 


        -  Start j loop from i+1


            -   if (intervals[j][0] <= end --> end = max(end, intervals[j][1] ))

                // if start can be accomodated --> end will be max of current and next pair (wrt expand)


            - else --> break;


     2.4 add (start, end) into answer array


```

### Code

```cpp

class Solution {

public:

    vector<vector<int>> merge(vector<vector<int>>& intervals) {


        int n = intervals.size();

        sort(intervals.begin(), intervals.end());


        vector<vector<int>> ans;


        for (int i = 0; i < n; i++){

            int start = intervals[i][0];

            int end = intervals[i][1];

            // can we accomodate this pair in last pushed pair in answer --> trying 1st type of overlap
            if (!ans.empty() && end <= ans.back()[1] ){
                // check if current end less than pushed end
                continue;
            }


            // trying second type of overlap on the [i+1]... intervals
            for (int j = i+1; j < n; j++){

                // type 2 overlap found
                if (intervals[j][0] <= end){
                    end = max(end, intervals[j][1]);
                }

                //type 3 found --> which is NO OVERLAP --> hence break
                else{
                    break;
                }
            }
            ans.push_back({start, end});
        }
        return ans;
    }

};

```

#### TC:
- Sort (nlogn)
- actually it is 2n based on the dry run
- --> FINAL = O ( 2n + n log n )

# Approch 2 - BETTER --> single iteration to remove double comparisons

- compare with last pushed pair in answer array
  - --> if we can accomodate the current pair --> edit range
  - --> if not --> add the current pair as a new one

```cpp

class Solution {

public:

    vector<vector<int>> merge(vector<vector<int>>& intervals) {


        int n = intervals.size();

        sort(intervals.begin(), intervals.end());


        vector<vector<int>> ans;


        for (int i = 0; i < n; i++){


            // 1. first pair OR this pair cant be merged --> ADD THIS PAIR IN ANS
            if (ans.empty() || intervals[i][0] > ans.back()[1]){
                ans.push_back(intervals[i]);
            }


            // 2. if not, then we will be editing the interval that has been pushed, since THIS interval is overlapping it

            else{
                ans.back()[1] = max (ans.back()[1], intervals[i][1]);
            }

        }
        return ans;
    }

};

```
