# Binary Search

*Five sub-patterns. If you get one thing solid here, make it **pattern 2 — "record the MAYBE answer"** — it is the seed of patterns 3 and 4 too. Code blocks are main logic only.*

---

## 1. Plain BS on a sorted array

**What it is:** the base move — halve a sorted array each step by comparing the middle to the target. **Why it works:** sortedness means one comparison tells you which half the answer *can't* be in, so you throw away half the search space per step → O(log n). **Trigger:** input is sorted (or monotonic) and you want an exact position or a yes/no. Everything else in this topic is this loop with one modification.

**Binary Search** — the literal template.

```cpp
while (low <= high){
    int mid = low + (high - low) / 2;
    if (nums[mid] == target){ return mid; }
    else if (nums[mid] > target){ high = mid - 1; }
    else{ low = mid + 1; }
}
return -1;
```

- **Time:** `O(log n)` — n = size of the array; each step halves the search space.
- **Space:** `O(1)` — only the three index variables.

**Square Root (floor)** — search the state space `1..x`. Twist: you want the **FLOOR**, so you *record* `mid` on the `< x` branch instead of returning.

```cpp
while(start <= end){
    mid = start + (end - start) / 2;
    double square = pow(mid, 2); // 1. use double because (2^31)^2 will go out of bound for int 
    if( square > x){
        end = mid - 1;
    }
    else if(square < x){
        start = mid + 1;
        result = mid; // 2. We are recording value as the formula calculates the "CEIL" --> and we need "FLOOR"
    }
    else{
        return mid;
    }
}
return result;
```

- **Time:** `O(log x)` — x = the input number; search space is `1..x`.
- **Space:** `O(1)` — only start/end/mid and the result.

---

## 2. Lower / upper bound — "record the MAYBE answer" ⭐

**What it is:** instead of returning on an exact match, you find the *boundary* — the first index whose value is `>= target` (lower bound) or `> target` (upper bound). **Why it's clever:** you never return early; every time `mid` *satisfies* the condition you save it as a candidate (`ans = mid`) and keep searching left for a tighter one. That save-then-keep-going is the most reusable idea in this topic — rotated search, Koko, and first/last-position are all this with a different condition. **Trigger:** "first element that…", "how many are less than…", "insert position", or any problem where the exact value may not exist.

**Lower & Upper Bound** — `ans = nums.size()` is the fallback for "target bigger than everything." Upper bound is the identical loop with `>` instead of `>=`.

```cpp
int ans = nums.size(); // hypothetical last position as ans --> needed when target is greater than all elements in array

while(low <= high){
    int mid = low + (high - low) / 2;

    if(nums[mid] >= target){ // satisfies cond. --> therefor this "MAYBE" the answer
        ans = mid;  // record the MAYBE answer
        high = mid - 1; // change search space for next iteration -- 1
    }
    else{   // it is less than target, hence, violates our condition, therefore not our answer
        low = mid + 1; // change search space for next iteration - 2
    }
}
return ans;
```

- **Time:** `O(log n)` — n = size of the array; halved each iteration.
- **Space:** `O(1)` — only the ans/low/high/mid variables.

**First and Last Position** — LB gives first, `UB - 1` gives last. Twist is the absence guard: LB can land at `n` or on a different value, so check both before trusting it.

```cpp
int low = lowerbound (nums, target);
int high = upperbound (nums, target);

// if elements ABSENT --> check if in bounds && check if it is target
if(low >= nums.size() || nums[low] != target){
    return {-1, -1};
}
// if elements are ACTUALLY present
else{
    return {low, high - 1};
}
```

- **Time:** `O(log n)` — n = size of the array; one lower-bound and one upper-bound pass.
- **Space:** `O(1)` — only the low/high index variables.

---

## 3. Search the answer space (not the array) ⭐

**What it is:** the array isn't what you binary-search — you binary-search a *range of possible answers* (a speed, a radius, a capacity). Pick a candidate `mid`, ask a boolean "is this feasible?", shrink toward the smallest feasible one. **Why it's the senior move:** it converts an optimization problem ("minimum eating speed") into O(n log(range)) by exploiting that feasibility is *monotonic* — if speed 5 works so does 6, if it fails so does 4. That monotonicity is what lets you binary-search something that isn't even a list. **Trigger:** "minimum/maximum X such that a condition holds," answer is a number in a known range, and you can write a `canDo(mid)` check.

**Koko Eating Bananas** — BS on eating speed. The feasibility check uses ceiling division `(pile + mid - 1)/mid` to model "must finish the hour"; low bound is tightened to `sum/h`.

```cpp
// feasibility check
int time = 0;
for(int i = 0; i < piles.size(); i++){
    int current_pile = piles[i];
// DIVIDE THE PILE to get the total hours required to finfish the pile
// Also use celing logic so that it does not floor the division value
    time += (current_pile + mid - 1) / mid;
    if (time > h) return false;
}
return true;

// the search
int low = (sum + h - 1) / h;
int current_lowest_k = high;
while(low <= high){
    int mid = (low + high) / 2;
    if (solution(piles, h, mid)){
        current_lowest_k = mid;   // record the MAYBE answer, then push left
        high = mid - 1;
    }
    else{
        low = mid + 1;
    }
}
return current_lowest_k;
```

- **Time:** `O(n log M)` — n = piles, M = max pile value; log over the speed range, n work per feasibility check.
- **Space:** `O(1)` — only the low/high/mid and time accumulator.

**Heaters** — a minimax. For each house, lower-bound the nearest heater on the right, check `idx-1` for the left, take the closer; the answer is the **max over houses of each house's min distance**.

```cpp
for(int house : houses){
    int idx = lb(heaters, house);       // lower bound --> nearest heater to the RIGHT

    long right_dist = LONG_MAX;
    if(idx != -1){
        right_dist = abs((long)house - (long)heaters[idx]);
    }

    long left_dist = LONG_MAX;
    int left_index;
    if(idx == -1){
        // no RHS heater --> rightmost heater is actually the LHS heater
        left_index = heaters.size() - 1;
    }
    else{
        left_index = idx - 1;
    }
    if(left_index >= 0){
        left_dist = abs((long)house - (long)heaters[left_index]);
    }

    long best_for_this_house = min(right_dist, left_dist);
    result = max(result, best_for_this_house);  // MAX of the MINs
}
```

- **Time:** `O(m log h)` — m = houses, h = heaters; one lower-bound lookup per house.
- **Space:** `O(1)` — only the per-house distance variables.

---

## 4. Pivot / rotated array — elimination by which half is sorted

**What it is:** a sorted array rotated once is two sorted runs stitched together. You can't compare `mid` to `target` directly, but at any `mid` **one side is always fully sorted** — so check "is `mid`'s sorted side the one containing target?" and eliminate accordingly. **Why it works:** even broken, half the array is orderly at every step, and an orderly half you can range-check in O(1). **Trigger:** "sorted but rotated" — find target, find min, or find the rotation point.

**Search in Rotated Sorted I** — identify the sorted half, range-check the target inside it, eliminate.

```cpp
if (nums[mid] == target) return mid;

// 1. check if left part is sorted 
if (nums[low] <= nums[mid]){
    if (nums[low] <= target && target  <= nums[mid]){
        high = mid - 1;
    }
    // Oh, thanks man for being sorted, but you were of no use. So I'll be going into the other part.
    else{
        low = mid + 1;
    }
}
// right is sorted
else{
    if (nums[mid] <= target && target  <= nums[high]){
        low = mid + 1;
    }
    else{
        high = mid - 1;
    }
}
```

- **Time:** `O(log n)` — n = size of the array; one sorted half is eliminated each step.
- **Space:** `O(1)` — only the low/mid/high index variables.

**Search in Rotated Sorted II** — duplicates break the "which half is sorted" test when `nums[low]==nums[mid]==nums[high]`. Twist is that dead case: you can't tell, so shrink *both* ends by 1 (worst case degrades to O(n)).

```cpp
if (nums[mid] == target) return true;

// extra crazy edge case handling 
if (nums[low] == nums[mid] && nums[mid] == nums[high]){
    low += 1;
    high -= 1;
    continue;
}
else if (nums[low] <= nums[mid]){ /* ...same as Part I... */ }
else{ /* ...same as Part I... */ }
```

- **Time:** `O(log n)` avg → `O(n)` worst — n = size of the array; duplicates force the `low+=1, high-=1` shrink.
- **Space:** `O(1)` — only the low/mid/high index variables.

**Minimum in Rotated Sorted** — compare `nums[mid]` to `nums[r]` to know which run you're in; record `ans` in **both** branches and drift toward the smaller run.

```cpp
int ans = INT_MAX;
while (l <= r){
    int mid = (l + r) / 2;
    if (nums[mid] <= nums[r]){          // mid in sorted portion
        ans = min(ans, nums[mid]);
        r = mid - 1;
    }
    else{                                // mid in rotated part --> min is further right
        ans = min (ans, nums[mid]);
        l = mid + 1;
    }
}
return ans;
```

- **Time:** `O(log n)` — n = size of the array; one comparison eliminates half each step.
- **Space:** `O(1)` — only the l/r/mid and ans variables.

**Find Pivot** — the clean boundary variant. Memorize this shape; it's the one people get wrong.

```cpp
while (low < high) {  // Note: < not <=
    int mid = low + (high - low) / 2;
    if (nums[mid] > nums[high]) {
        low = mid + 1;      // pivot in right half
    }
    else {
        high = mid;         // Note: NOT mid - 1
    }
}
return nums[low];  // low == high == pivot
```

- **Time:** `O(log n)` — n = size of the array; strict `<` loop still halves each step.
- **Space:** `O(1)` — only the low/mid/high index variables.

---

## 5. Staged BS (2D)

**What it is:** a matrix sorted so each row's first element beats the previous row's last — effectively a flattened sorted array. BS twice: first on the first column to find the candidate row, then inside that row. **Why the staging helps:** each stage stays a plain 1-D binary search instead of forcing index math on a virtual flattened array. **Trigger:** "search a sorted matrix" where rows and columns both ascend and rows don't overlap.

**Binary Search in Matrix** — pass 1 finds the row by range-check; if none, bail *before* pass 2.

```cpp
// STAGE 1 --> find the row
int final_row = -1;
while (top_row <= bottom_row){
    int mid = (top_row + bottom_row ) /2;
    if (target >= matrix[mid][0] && target <= matrix[mid][n]){
        final_row = mid;
        break;
    }
    else if (target < matrix[mid][0]){ bottom_row = mid - 1; }
    else{ top_row = mid + 1; }
}

// VERY IMPORTANT --> this means that our first loop did not find a valid row and ended 
if (final_row == -1) return false;

// STAGE 2 --> plain BS inside that row
while(low <= high){
    int mid = (low + high ) /2;
    if (target == matrix[final_row][mid]){ return true; }
    else if (target < matrix[final_row][mid]){ high = mid - 1; }
    else{ low = mid + 1; }
}
return false;
```

- **Time:** `O(log r + log c)` — r = rows, c = columns; one BS to find the row, one BS inside it.
- **Space:** `O(1)` — only the row/low/high/mid index variables.

---

*Thread out of this topic: **"record the MAYBE answer"** (pattern 2) is the engine behind patterns 3 and 4 — save the candidate, keep shrinking. Carry it into Sliding Window — "binary-search anchor then expand", where a BS anchor sets up a two-pointer expansion.*
