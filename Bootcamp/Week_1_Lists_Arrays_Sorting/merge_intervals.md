Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

Example 1:

Input: intervals = [[1,3],[2,6],[8,10],[15,18]]

Output: [[1,6],[8,10],[15,18]]

Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

Example 2:

Input: intervals = [[1,4],[4,5]]

Output: [[1,5]]

Explanation: Intervals [1,4] and [4,5] are considered overlapping.

Example 3:

Input: intervals = [[4,7],[1,4]]

Output: [[1,7]]

Explanation: Intervals [1,4] and [4,7] are considered overlapping.

---

## INTUITION

- maybe needs sorting every pair and then traverse
- but sorting would not sort all the pairs inside our list --> so simple traversing would not work on example 3

--> JUST IN --> based on the constraint 0 <= starti <= endi <= 104 --> internal pairs are always sorted

## BRUTE

- SOMEHOW if I am able to sort the pairs by inner first element --> then we can do something
- 

Eg:

1,2 1,9 8,10

- 2 pointer approach
- if (intervals[i+1][0] <= intervals[i][1] --> merge)

--> Also need to write how to merge:

**CANT DO**

# STRIVER

## Brute --> Sort (default sort does everything) and traverse

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

            // can we accomodate this pair in last pushed pair in answer
            if (!ans.empty() && end <= ans.back()[1] ){
                // check if current end less than pushed end

                continue;

            }


            for (int j = i+1; j < n; j++){
                if (end >= intervals[j][0]){

                    end = max(end, intervals[j][1]);

                }

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

TC -->

- Sort (nlogn)
- actually it is 2n based on the dry run
- --> FINAL = O ( 2n + n log n )

## BETTER --> single iteration to remove double comparisons

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
