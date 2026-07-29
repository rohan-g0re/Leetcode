# Sliding Window

*Five sub-patterns, and they form a ladder: fixed width, then variable width where the left edge **jumps**, then variable width where validity is a **formula**. That third one (3) is the load-bearing pattern and holds the single sharpest insight in this whole document. Code blocks are main logic only.*

---

## 1. Fixed window with a set

**What it is:** a window of fixed width slides across the array, and a hash-set holds exactly the elements currently inside it — so "is there a duplicate within distance k" becomes an O(1) membership test.

**Why the set:** it turns "look back k elements" from a k-step scan into a single lookup. The bookkeeping that keeps it honest is the eviction — before you test the new element, you must delete the one that just fell out the back, or your set slowly becomes "everything I've ever seen" and starts lying to you.

**Where it shows up:** "within k indices," "in any window of size k," or a fixed-span membership question. The moment the window width is a constant given in the problem, this is the shape.

**Contains Duplicate II** — the set *is* the window contents; evict `nums[i-k-1]` before testing.
```cpp
for(int i = 0; i < n; i++){
    // 1. remove in valid number before comparing
    if (window.size() > k) window.erase(nums[i - k - 1]);

    // 2. compare the current number with set
    if (window.find(nums[i]) != window.end()) return true;

    // 3. insert this number in set
    window.insert(nums[i]);
}
return false;
```

- **Time:** `O(n)` — n = length of nums; one pass, each index processed once.
- **Space:** `O(k)` — set holds at most k elements, the window width.

---

## 2. Longest valid window + map of last-seen index

**What it is:** a *variable* window where the left edge doesn't creep forward one step at a time — it **jumps** straight past the last occurrence of the repeated character. A `char → last index` map tells it exactly how far to leap.

**Why the jump matters:** the naive fix on a repeat is to shrink from the left until the duplicate is gone, which in the worst case re-walks the whole window and lands you at O(n²). Jumping `l = lastSeen + 1` gets you to the same place in one assignment, so both pointers only ever move forward and the whole scan stays O(n). **Each pointer moves forward only — that's the budget that buys you linear time.**

**Where it shows up:** "longest substring without repeating characters" and every variant of it — longest span satisfying a uniqueness constraint.

**Longest Substring Without Repeating Characters** — the twist that people miss is the `< l` guard. A character sitting in the map from *before* the current window is stale, and if you trust it blindly you drag `l` backward and start counting a window that no longer exists.
```cpp
while (r < n){
    // case 1: not in map --> add    | case 2: in map BUT outside window (stale) --> update
    if (mp.find(s[r]) == mp.end() || mp[s[r]] < l ){
        mp[s[r]] = r;
    }
    // case 3: in map && inside window --> JUMP l past it, then update
    else if(mp[s[r]] >= l){
        l = mp[s[r]] + 1;
        mp[s[r]] = r;
    }

    max_length = max(max_length, r - l + 1);
    r++;
}
```

- **Time:** `O(n)` — n = length of s; both pointers only ever move forward.
- **Space:** `O(min(n, alphabet))` — map stores at most one index per distinct character.

---

## 3. Window + frequency, validity as arithmetic ⭐

**What it is:** the window carries a frequency count, and "is this window still valid?" stops being a scan and becomes a formula. For character replacement it's `window_length - maxFreq <= k` — the letters you'd have to change must fit inside your budget.

**Why the stale-`maxf` trick is the gem:** the obvious worry is that when you shrink the window, `maxf` might now be too high, and you've stopped recomputing it. That's true — and it's *safe*. A too-high `maxf` only makes the window look valid, never invalid, so you can't lose a real answer; and you only ever record `res` when the window is **longer** than anything before, which requires `maxf` to have genuinely grown. So an inflated `maxf` can inflate the window's apparent validity but can never inflate the recorded answer. **That one observation is the entire problem** — it turns an O(26n) recompute into an O(n) pass, and explaining *why* it's safe is the answer that sounds like you've actually thought about it rather than memorized it.

**Where it shows up:** "longest window with at most k changes / k violations / k flips." Whenever the constraint can be written as arithmetic over the window's counts instead of a re-scan, you're here.

**Longest Repeating Character Replacement** — shrink only while `(r-l+1) - maxf > k`; `maxf` is never rolled back.
```cpp
int l = 0, maxf = 0;
for (int r = 0; r < s.size(); r++) {
    count[s[r]]++;
    maxf = max(maxf, count[s[r]]);    // never decreased --> provably safe

    while ((r - l + 1) - maxf > k) {  // too many chars would need replacing
        count[s[l]]--;
        l++;
    }
    res = max(res, r - l + 1);
}
```

- **Time:** `O(n)` — n = length of s; maxf is never recomputed, just tracked forward.
- **Space:** `O(1)` — count array is fixed at 26 letters, a constant-size alphabet.

---

## 4. Two pointers that never reset

**What it is:** a degenerate window where the right pointer marches on unconditionally and the left pointer only ever *jumps to* the right pointer — and only when it finds something strictly worse.

**Why it's still a window:** you're tracking the best "buy low, sell high" span, and the left pointer is your buy point. There's no reason to keep an old buy price once you've seen a cheaper one, because any future sale profits more from the lower buy. So the reset isn't shrinking, it's **abandoning a dominated candidate.**

**Where it shows up:** "best profit from a single buy and sell," "max difference where the smaller element must come first," and any single-pass min-tracking problem.

**Best Time to Buy and Sell Stock** — `l` resets to `r` only on a dip; `r` always advances.
```cpp
while(r < n){
    if (prices[r] > prices[l]){
        profit = max (profit, prices[r] - prices[l]);
    }
    else{
        l = r;   // found a cheaper buy point --> abandon the old one
    }
    r++; // r increments any-which-ways --> unlike l which changes only when we find a dip
}
```

- **Time:** `O(n)` — n = length of prices; both pointers only ever move forward.
- **Space:** `O(1)` — only `l`, `r`, and `profit` are tracked, no extra structure.

---

## 5. Binary-search anchor, then expand outward

**What it is:** not a contiguous window at all. You binary-search the *insertion point* of a target to find the center, then grow a two-sided selection outward, always taking whichever neighbor is closer.

**Why the hybrid:** binary search gets you to the center in O(log n) — scanning for it would already cost O(n) and waste the sortedness. Then the outward expansion picks the k best in O(k), because in a sorted array the k closest elements are always a **contiguous block** containing the anchor, so comparing the two frontiers is enough. **You never need to look anywhere except the two edges of what you've taken.**

**Where it shows up:** "k closest elements to x," "k elements around a value," and range-selection problems on sorted input. It's also a nice bridge — Binary Search — "lower/upper bound" is doing the anchoring here.

**K Closest Elements** — anchor by lower-bound BS, then two pointers pick the closer side each step. Twist is the tie rule (favor left) and the final sort, since you collect out of order.
```cpp
int index = binary_search(arr, x);   // lower-bound anchor

int r = (index < n) ? index : n;
int l = r - 1;   // could be -1, guarded by the loops

while(k > 0 && l >= 0 && r < n){
    if ( abs (arr[l] - x) <= abs(arr[r] - x) ){  // picking the left when a tie happens
        result.push_back(arr[l]);
        l--;
    }
    else{
        result.push_back(arr[r]);
        r++;
    }
    k--;
}

// one side ran out --> drain the other
while (k > 0 && l >= 0){ result.push_back(arr[l]); l--; k--; }
while (k > 0 && r < n){ result.push_back(arr[r]); r++; k--; }

sort(result.begin(), result.end());
```

- **Time:** `O(log n + k log k)` — log n to anchor by binary search, k log k to sort k results.
- **Space:** `O(k)` — result holds exactly the k output elements.

---

*Threads out of this topic: 3's never-decreasing `maxf` is the **monotonic invariant** from Stacks — "monotonic stack" in disguise — keep the boundary quantity reachable, don't recompute it. 2's last-seen map is the **hash-as-O(1)-memory** thread from Array Hashing. And 5 hands straight back to Binary Search — "lower/upper bound".*
