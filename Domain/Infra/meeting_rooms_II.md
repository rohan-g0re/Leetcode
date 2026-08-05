# LC 253 - Medium

## Intuition:
1. Total rooms being used is the current size of the heap.
2. There are only 2 ways to get a room:
    1. REUSE A MEETING ROOM - if the meeting in it has ended --> pop it oput of heap and push our new meeting slot 
        --> heap size stays the same -- this is the equivalent of reusing room 
    2. USE A NEW ROOM --> this will increase the size 

#### This procedure in itself is the only optimal way of maximizing the use of rooms --> Hence, this is GREEDY & OPTIMAL.

# IMP 1. LAMBDA COMPARATOR

```cpp
sort(intervals.begin(), intervals.end(), [](Interval& a, Interval& b){
    return a.start < b.start;
});
```

### 1. Why empty `[]` ?
- `[]` = **capture list** --> how the lambda pulls variables from **outside**
- example: `[&cap]` or `[cap]` would bring an outside variable `cap` into the lambda
- here `[]` is empty --> we capture **nothing**
- we dont need outside values --> because `a` and `b` are already passed **as arguments**

### 2. What scope are `a` and `b` ?
- NOT the whole array as one object
- `sort` picks **two individual `Interval` objects** from the vector and hands them to the comparator
- that is why we have two params: `Interval& a` and `Interval& b`
- each call = compare one pair of meetings

### 3. Why compare `start` ?
- we want meetings processed in **start-time order**
- greedy needs earliest-starting meeting first --> so we can decide reuse vs new room correctly
- `return a.start < b.start` --> **Does a rank before b?** --> yes if a starts earlier

# IMP 2. Object access

### WHY `meet -> start` IS WRONG HERE

You wrote `meet -> start` thinking like LL:
- LL: `ListNode* mover` --> pointer --> so `mover -> val`, `mover -> next` is correct
- here: `for(auto& meet : intervals)` --> `meet` is a **reference to an Interval object** (a value), NOT a pointer

#### THE RULE
- **pointer** (`Interval*` / `Node*`) --> use `->`
- **object / reference** (`Interval` / `Interval&`) --> use `.`

```cpp
Interval* p = ...;   // pointer  --> p -> start
Interval  x = ...;   // object   --> x.start
Interval& r = x;     // reference to object --> r.start   (SAME as object)
```

### "But in LL, next/val are also just values of the object — why arrow there?"

Yes — `val` and `next` are fields either way. The arrow is **not** about "getting a field". The arrow is about **how you hold the object**:

- LL node is almost always held as `Node*` (address in memory)
- so you dereference + access field in one step: `pointer -> field`
- `meet` here is already the Interval itself (via `&`) --> no dereference needed --> `meet.start`



## SHORT MENTAL MODEL
- `->` means: "I have an **address**, go there, then read the field"
- `.` means: "I already have the **object**, just read the field"

`meet -> start` fails because `meet` is not an address.





# Code:

```cpp
#include <bits/stdc++.h>
/**
 * Definition of Interval:
 * class Interval {
 * public:
 *     int start, end;
 *     Interval(int start, int end) {
 *         this->start = start;
 *         this->end = end;
 *     }
 * }
 */

class Solution {
public:
    int minMeetingRooms(vector<Interval>& intervals) {
        

        sort(intervals.begin(), intervals.end(), [](Interval& a, Interval& b){
            return a.start < b.start;
        });


        // heap size gives you meeting rooms

        priority_queue<int, vector<int>, greater <int>> min_heap;
        int result = 0;

        for(auto& meet : intervals){
            
            // if we can reuse the room we make it empty
            if(!min_heap.empty() && min_heap.top() <= meet.start){
                min_heap.pop();
            }

            // EITHERWAYS - we use the room 
            min_heap.push(meet.end);

            result = max(result, (int)min_heap.size());
        }
        return result;      
    }
};

```