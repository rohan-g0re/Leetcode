# Heaps

*Three sub-patterns, and they are genuinely three different jobs a heap does: it answers "what's the k-th," it feeds a greedy simulation, and it merges sorted streams. The one to say out loud in an interview is **1 — for k-th largest you use a min-heap** — because getting the type backwards is the classic tell. Code blocks are main logic only.*


### Syntax:

###### 1. MIN_HEAP --> required to get the kth largest element

```cpp
priority_queue <pair<int, int>, // declare datatype 
vector<pair<int, int>>, // container --> basically datatype wrapped inside vector
greater <pair<int, int>> // comparator --> basically datatype again
> min_heap;
```

###### MAX_HEAP --> required to get the kth smallest element

```cpp
// The default is max heap so just need to give datatype of every node in heap 
priority_queue <pair<int, int>> max_heap;

```




---

## 1. Size-K heap for Kth / Top-K (use the *opposite* type) ⭐

**What it is:** to find the **k-th largest**, you keep a **min-heap of size k**. The moment it overflows you pop the smallest, so the k biggest survive and the k-th largest sits at the top, one peek away.

**Why the opposite type is the trick:** a min-heap's cheapest operation is "evict the smallest," which is exactly what you want when you're hunting large values — everything small gets thrown out for free. You spend O(n log k) instead of O(n log n), and you never hold more than k items in memory, which matters when the input is a stream you can't store. The detail that sounds experienced: say *"for k-th largest I use a min-heap of size k, because then the answer is always `heap.top()`"* — the alternative, a max-heap of size n, forces you to pop k times just to read the answer.

**Where it shows up:** any time the question says "k-th," "top k," or "k closest" and k is much smaller than n. You'll notice the heap is doing the same job as Stacks — "the monotonic stack" — keeping the boundary element permanently reachable so you never re-scan.

**Kth Largest in a Stream** — the class-based version. Pre-seed the size-k min-heap in the constructor; every `add` pushes-then-trims and returns the top.
```cpp
// constructor --> pre-seed
for(int element : nums){
    heap.push(element);
    if (heap.size() > kx) heap.pop();
}

// add() --> push, trim, peek
heap.push(val);
if (heap.size() > kx) heap.pop();
return heap.top();
```

- **Time:** `O(n log k)` — n = initial stream size for setup; each `add()` costs `O(log k)`.
- **Space:** `O(k)` — heap never holds more than the k largest elements.

**Kth Largest in an Array** — the same idea one-shot. Your own note captures the whole decision:
```cpp
/*
1. either you have a min heap -- keep it of size k -- and for answer you have to pop ONLY TOP element  
2. You have a max heap -- keep it of n size -- and for answer you would need to pop k elements  
*/
for (int num : nums){
    min_heap.push(num);
    if (min_heap.size() > k){ min_heap.pop(); }
}
return min_heap.top();
```

- **Time:** `O(n log k)` — n = array size; heap capped at k, each push/pop costs log k.
- **Space:** `O(k)` — heap never grows past k elements.

**K Closest Points to Origin** — flip the type: a size-k **max**-heap keyed by distance, so the *farthest* gets evicted. Twist is the composite key `pair<double, pair<int,int>>` — the heap orders on distance while still carrying the coordinates you have to return.
```cpp
priority_queue< pair<double, pair<int, int>> > max_heap;

for (auto& pair : points){
    int x = pair[0];
    int y = pair[1];
    double distance = sqrt ((pow(x, 2)) + pow(y, 2) );

    max_heap.push({distance, {x, y}});
    if (max_heap.size() > k) max_heap.pop();   // drop the farthest
}
```

- **Time:** `O(n log k)` — n = points; each push/pop on the size-k heap costs log k.
- **Space:** `O(k)` — heap holds only the k closest points.

---

## 2. Greedy simulation with a heap

**What it is:** you repeatedly need "the current best" while the set of candidates keeps changing — so the heap hands you the extreme element each round, you act on it, and you push the modified result back in.

**Why a heap and not a sort:** a one-time sort goes stale the instant you change something. You smash two stones and produce a *new* stone; you run a task and its frequency *drops*; you earn capital and *more* projects become affordable. The heap re-surfaces the new best in O(log n) after every mutation, which a sorted array can't do without re-sorting. The mental model: **a sort is a photograph, a heap is a live feed.**

**Where it shows up:** the giveaway phrasing is "repeatedly take the largest/smallest, do something, and possibly put a new value back." If the candidate set were frozen you'd sort once and walk it; the moment the round changes the set, you need the heap.

**Last Stone Weight** — max-heap; smash the two heaviest, re-insert the difference. Twist is the *conditional* re-push — equal stones both vanish and nothing goes back.
```cpp
while (!max_heap.empty()){
    if (max_heap.size() == 1) return max_heap.top();

    int y = max_heap.top(); max_heap.pop();
    int x = max_heap.top(); max_heap.pop();

    if (x == y){ continue; }
    else{ max_heap.push( abs(y-x) ); }
}
return 0;
```

- **Time:** `O(n log n)` — n = stones; each of the ~n rounds does O(log n) push/pop.
- **Space:** `O(n)` — heap can hold up to n stones.

**Task Scheduler** — the dual-structure gem, and the most interview-worthy code in this topic: a **max-heap of ready tasks** plus a **cooldown queue** of `{freq, unlock_time}`. The twist that makes it correct is looping while *either* structure is non-empty — an empty heap doesn't mean you're done, it means everyone is cooling and this tick is an idle.
```cpp
while (!max_heap.empty() || !queue.empty()){
    // STEP 1: if valid node in queue add it in heap
    if (!queue.empty() && queue.front().second == time){
        max_heap.push ( queue.front().first );
        queue.pop();
    }

    // STEP 2: nobody is SCHEDUL-ABLE --> IDLE --> burn a tick
    if (max_heap.empty()){ time++; continue; }

    // STEP 3: run the most frequent ready task
    int task_freq = max_heap.top();
    max_heap.pop();
    time++;
    int new_freq = task_freq - 1;

    // STEP 4: send it to cool down, only if runs remain
    if (new_freq > 0) queue.push({new_freq, time + n});
}
return time;
```

- **Time:** `O(n log k)` — n = total tasks run, k = distinct task types (≤26); each heap op costs log k.
- **Space:** `O(k)` — heap and cooldown queue hold at most k task types.

**IPO** — sort projects by capital, then walk a pointer that **lazily unlocks** every newly-affordable project into a max-heap of profits, and take the top. Twist is the sorted-array-plus-pointer-plus-heap combo: the pointer never rewinds, so across all k rounds you touch each project exactly once instead of re-scanning the list every round.
```cpp
sort(main_array.begin(), main_array.end());   // by capital
int mover = 0;

for(int i = 0; i < k; i++){
    // increment mover until capital[mover] becomes invalid
    while (mover < main_array.size() && main_array[mover].first <= w){
        max_heap.push(main_array[mover].second);   // unlock affordable projects
        mover++;
    }

    if(!max_heap.empty()){ w += max_heap.top(); max_heap.pop(); }
    else{ return w; }   //we did not move --> hence no valid task left
}
return w;
```

- **Time:** `O(n log n)` — n = projects; sort dominates, mover pushes/pops each n items once at O(log n).
- **Space:** `O(n)` — max-heap can hold up to n unlocked projects.

---

## 3. Heap as the front line of k sorted sequences

**What it is:** to merge k already-sorted sequences, you hold only the *current front* of each one in a heap. Pop the global smallest, emit it, then push that sequence's next element to take its place.

**Why it beats concatenate-then-sort:** you're exploiting the fact that each list is already ordered — the global minimum can only ever be one of the k heads, so you never need more than k candidates in memory. That gives O(N log k) instead of O(N log N), and the space stays at k no matter how long the lists are. Think of it as **k queues at a counter, and you always serve whoever's front person is smallest.**

**Where it shows up:** "merge k sorted lists," "smallest range covering all lists," or external sorting where the inputs are files too big to load. If you ever catch yourself about to flatten k sorted things and re-sort, this is the pattern you skipped.

**Merge K Sorted Linked Lists** — min-heap of `pair<int, ListNode*>`: the value drives the ordering, the pointer lets you advance into that specific list in O(1) after popping.
```cpp
// seed with every list's head
for(auto& ele : lists){
    if(ele != nullptr){ min_heap.push({ele -> val, ele}); }
}

while(!min_heap.empty()){
    int current_val = min_heap.top().first;
    ListNode* Node = min_heap.top().second;
    min_heap.pop();

    // create - append - move in answer - move in LL
    ListNode* temp = new ListNode(current_val);
    mover -> next = temp;
    mover = mover -> next;
    Node = Node -> next;

    if(Node != nullptr){ min_heap.push({Node -> val, Node}); }   // push that list's next front
}
return dummy-> next;
```

- **Time:** `O(N log k)` — N = total nodes across all lists, k = number of lists; each pop/push costs log k.
- **Space:** `O(k)` — heap holds at most one node per list at a time.

*(Notice this is also the **dummy node** pattern from Linked Lists — "Dummy node" — the heap only decides the order, the dummy does the building.)*

---

*Thread out of this topic: the **monotonic invariant** again — a heap, like Stacks — "the monotonic stack", is a structure that keeps the element you care about permanently at the boundary so you never rescan. And pattern 3 hands you straight into Linked Lists — "Dummy node", where the same dummy-node build shows up without the heap.*
