## INTUITION

#### 1. calculate distance from origin 
#### 2. push distance in min heap

```bash
----

BUT the closest k points would keep on changing ---> so we need to keep a map of {distance, coordinates}

```

*******

#### DUMB --> we can create the queue to have distance as well as coordinates



# IMPORTANT 1 --> if we have distance as int, it will not give accurate results while comparing small values (because they round off) --> if we use float it cant handle the overflow resulting by 9999^2 (i guess) --> thereofr use double





```cpp

class Solution {
public:
    vector<vector<int>> kClosest(vector<vector<int>>& points, int k) {

        priority_queue< pair<double, pair<int, int>> > max_heap;

        for (auto& pair : points){

            int x = pair[0];
            int y = pair[1];

            double distance = sqrt ((pow(x, 2)) + pow(y, 2) );

            max_heap.push({distance, {x, y}});

            if (max_heap.size() > k) max_heap.pop();

        }

        vector <vector<int>>result;

        while(!max_heap.empty()){

            result.push_back({max_heap.top().second.first, max_heap.top().second.second});
            max_heap.pop();

        }
        
        return result;
    }
};

```