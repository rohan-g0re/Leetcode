# LC 362 - Medium

### Description

Design a hit counter which counts the number of hits received in the past 5 minutes (i.e., the past 300 seconds).

Your system should accept a `timestamp` parameter (in **seconds** granularity), and you may assume that calls are being made to the system in chronological order (i.e., `timestamp` is monotonically increasing). Several hits may arrive roughly at the same time.

Implement the `HitCounter` class:

- `HitCounter()` Initializes the object of the hit counter system.
- `void hit(int timestamp)` Records a hit that happened at `timestamp` (in seconds). Several hits may happen at the same `timestamp`.
- `int getHits(int timestamp)` Returns the number of hits in the past 5 minutes from `timestamp` (i.e., the past `300` seconds).

### Example 1

```
Input
["HitCounter", "hit", "hit", "hit", "getHits", "hit", "getHits", "getHits"]
[[], [1], [2], [3], [4], [300], [300], [301]]
Output
[null, null, null, null, 3, null, 4, 3]

Explanation
HitCounter hitCounter = new HitCounter();
hitCounter.hit(1);       // hit at timestamp 1.
hitCounter.hit(2);       // hit at timestamp 2.
hitCounter.hit(3);       // hit at timestamp 3.
hitCounter.getHits(4);   // get hits at timestamp 4, return 3.
hitCounter.hit(300);     // hit at timestamp 300.
hitCounter.getHits(300); // get hits at timestamp 300, return 4.
hitCounter.getHits(301); // get hits at timestamp 301, return 3.
```


## Intuition: basic brooo... --> the length from pointer to end is the valid range --> hence maintain the pointer as global variable ~ across methods


## Code

```cpp
class HitCounter {
private:
    vector<int> hitlist;
    int pointer;

public:
    HitCounter() {pointer = 0;}
  
    void hit(int timestamp) {
        hitlist.push_back(timestamp);
        return;
    }
  
    int getHits(int timestamp) {
        int n = hitlist.size();
        
        // the llop condition handles positive{gethit(500) = +200} and negative {gethit(4) = -296} acceptable floors--> Because in any case, we are supposed to stop when we get a bigger value than floor
        while(pointer < n && hitlist[pointer] <= timestamp - 300){
            // keep on iterating
            pointer++;
        }

        // there can be 2 reasons the above loop ended --> we got valid hitlist in 300 window --OR-- we reached the end of internet 
        if(pointer >= n) return -1;
        
        return n - pointer;
    
    }
};

/**
 * Your HitCounter object will be instantiated and called as such:
 * HitCounter* obj = new HitCounter();
 * obj->hit(timestamp);
 * int param_2 = obj->getHits(timestamp);
 */
```
