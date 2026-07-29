# Two Pointers

*Six sub-patterns. They split cleanly into pointers that **converge** (1, 2, 5), pointers where one **reads** and one **writes** (3, 4), and pointers that walk **separate inputs** (6). The load-bearing one is 2 — fix one element, two-pointer the rest — because it's the answer to the entire k-sum family. Code blocks are main logic only.*

---

## 1. Opposite ends converging

**What it is:** one pointer at each end, walking inward, deciding at each step which side to move based on a comparison.

**Why it's O(n) and not O(n²):** every element gets visited once in total, and the comparison guarantees you never have to go back to a side you already moved past. That guarantee is the whole thing — it only holds when moving a pointer can be *proven* not to discard the answer, which is why this pattern needs sorted input or a monotonic quantity like width.

**Where it shows up:** sorted array plus a pair/target condition, palindromes, or any area/width tradeoff. If the brute force is "check every pair," ask whether a converging scan can rule out half of them for free.

**Container With Most Water** — the width shrinks no matter which pointer you move, so you always move the **shorter** wall inward. Moving the taller one can never help: the height is capped by the shorter wall either way, and you'd have lost width for nothing. **That proof is the answer the interviewer wants, not the code.**
```cpp
while (L <= R){
    int length = R - L;
    int z_height =  min (height[L], height[R]);
    max_area = max (max_area, length * z_height);

    if ( height[L] < height[R]){ L++; }   // move the SHORTER wall
    else{ R--; }
}
```

- **Time:** `O(n)` — n = array length; pointers converge, each index visited once.
- **Space:** `O(1)` — two index variables and a running max, nothing allocated.

**Reverse String** — opposite-ends swap. Twist is only that you wrote it recursively instead of as a loop; the pointer logic is identical.
```cpp
if (l >= r){ return; }
swap (s[l], s[r]);
my_function(s, ++l, --r);
```

- **Time:** `O(n)` — n = string length; each recursive call swaps one pair and recurses inward.
- **Space:** `O(n)` — recursive, so the call stack holds n/2 frames, not O(1).

---

## 2. Fix one, two-pointer the rest (k-sum) ⭐

**What it is:** to find triplets (or k-tuples) that hit a target, you sort, **fix the outer element** with a loop, and run an opposite-ends two-pointer over what remains.

**Why sorting unlocks it:** in a sorted remainder the pair sum is monotonic — too big means the right pointer must come left, too small means the left pointer must go right. There's no guessing and no revisiting, so each fixed element costs O(n) instead of O(n²), taking 3Sum from O(n³) to O(n²). Sorting also makes duplicates *adjacent*, which is the only reason you can skip them by value instead of deduping with a set afterward. **Sorting buys you two things at once: a direction to move, and duplicates you can skip.**

**Where it shows up:** 2Sum on a sorted array, 3Sum, 4Sum, "find tuples that hit a target." Recognizing that k-sum is just (k-2) nested loops wrapped around this core is what makes the family feel small instead of endless.

**Three Sum** — fix `i`, two-pointer `j`/`k`. The practitioner's detail is buried in your own comment: the **manual `j++`/`k--` after recording a triplet** is what makes the duplicate-skipping while-loops behave. Without it, on an input with no duplicates those loops never advance and you spin.
```cpp
sort(nums.begin(), nums.end());

for (int i = 0; i < n - 2; i++){
    // Skip duplicate values for i
    if (i > 0 && nums[i] == nums[i-1]) { continue; }

    int j = i + 1;
    int k = n - 1;

    while (j < k){
        int sum  = nums[i] + nums[j] + nums[k];

        if (sum > 0){ k--; }        // too big --> shrink from the right
        else if (sum < 0){ j++; }   // too small --> grow from the left
        else{
            result.push_back({nums[i], nums[j], nums[k]});

// IMPORTANT -->> This manual increment is VERY IMP because --> THIS HANDLES THE CASE WHERE IT HAS NO DUPLICATES --> hence as we would have incremented/decremented manually, the while cases below WOULD NOT TRIGGER 
            j++;
            k--;

            while(nums[j] == nums[j-1] && j < k){ j++; }
            while(nums[k] == nums[k+1] && j < k){ k--; }
        }
    }
}
```

- **Time:** `O(n²)` — n = array length; sort is O(n log n), dominated by the outer loop times the inner scan.
- **Space:** `O(log n)` — sort's recursion stack; result triplets not counted as extra space.

**Two Sum II (sorted)** — the base case of the above, with no outer loop. Twist is the constraints: O(1) space, so no hash map allowed, and the output is 1-indexed.
```cpp
while (start < end){
    if (numbers[start] + numbers[end] < target){ start++; continue; }
    else if (numbers[start] + numbers[end] > target){ end--; continue; }
    return {start + 1, end + 1};   // 1-indexed
}
return {};
```

- **Time:** `O(n)` — n = array length; pointers converge, each index visited once.
- **Space:** `O(1)` — two index variables, no hash map allowed by the constraints.
*(Compare this to Array Hashing — "complement lookup" — unsorted Two Sum needs a hash map because there's no direction to move. Sorted input replaces O(n) space with a comparison.)*

---

## 3. Read pointer + write pointer (in-place)

**What it is:** a fast **read** pointer scans forward while a slow **write** pointer marks where the next kept element belongs, so the array compacts itself with no extra memory.

**Why it works:** everything before the write pointer is already the finished answer, and everything the read pointer has passed is either copied or discarded — so the two regions never conflict. You only advance the write pointer when the reader finds something worth keeping, which means the write pointer's final position *is* the answer's length.

**Where it shows up:** "remove / dedup / compact in place, return the new length." The tell is a problem that hands you an array and asks for a length back instead of a new array.

**Remove Duplicates from Sorted Array** — the slow pointer is the write head; advance and copy only on a genuinely new value.
```cpp
int pointer1 = 0;
int pointer2 = 1;
int count = 1; // because first element is always unique

while (pointer2 < nums.size()){
    // found duplicate that is already added
    if(nums[pointer2] == nums[pointer2 - 1] && nums[pointer2] == nums[pointer1]){
        pointer2++;
        continue;
    }
    // found unique --> write it
    else if (nums[pointer2] != nums[pointer2 - 1] && nums[pointer2] != nums[pointer1]){
        count++;
        pointer1++;
        nums[pointer1] = nums[pointer2];
        pointer2++;
    }
}
return count;
```

- **Time:** `O(n)` — n = array length; read pointer scans forward once.
- **Space:** `O(1)` — compacts in place, write pointer only, no extra array.

**Remove Element** — the order-not-preserved variant, and a nice example of reading the constraints for free wins. Because order doesn't matter, you swap a `val` at the front with a non-`val` from the back instead of shifting everything left — turning what could be O(n²) of shifting into a single converging pass.
```cpp
while (l <= r){
    if (nums[l] == val && nums[r] != val){
        swap(nums[l], nums[r]);
        l++;
        r--;
        continue;
    }
    else if (nums[l] != val) l++;
    else if (nums[r] == val) r--;
}
return l;
```

- **Time:** `O(n)` — n = array length; pointers converge, each index visited once.
- **Space:** `O(1)` — in-place swaps, no extra array allocated.

---

## 4. Fill from the back

**What it is:** when you're merging into an array that already has spare room at the end, you write **largest-first, starting from the tail.**

**Why the direction flip is the trick:** filling front-to-back would clobber `nums1` values you haven't read yet — you'd destroy the input while consuming it. Going back-to-front, the write head sits in the empty trailing space and only ever moves into territory you've already read, so a collision is impossible. **The spare room at the end isn't padding, it's the safe zone that makes in-place merging work.**

**Where it shows up:** "merge into this array in place," or any problem where the destination is also a source and has trailing capacity.

**Merge Sorted Array** — write pointer at `m+n-1`, compare tails, copy the bigger. Only `nums2`'s leftovers need draining; leftover `nums1` elements are already sitting in their correct positions.
```cpp
int l = m-1;
int r = n-1;
int write_pointer = m + n - 1;

while(l >= 0 && r >= 0){
    if (nums1[l] >= nums2[r]){ nums1[write_pointer] = nums1[l]; l--; }
    else{ nums1[write_pointer] = nums2[r]; r--; }
    write_pointer--;
}

// if nums 1 is longer --> we dont need to copy elements as they are already there
// if nums 2 is longer --> we need to copy elements
while(r >= 0){ nums1[write_pointer] = nums2[r]; write_pointer--; r--; }
```

- **Time:** `O(m+n)` — m, n = lengths of nums1, nums2; each element written exactly once.
- **Space:** `O(1)` — merges into nums1's own trailing capacity, no new array.

---

## 5. Skip-and-compare (palindromes)

**What it is:** ends-inward comparison, except you get one "life" — on a mismatch, try skipping the left character *or* the right one and check whether either remainder is a clean palindrome.

**Why the branch is enough:** with at most one deletion allowed, the **first** mismatch is your only decision point. Everything before it already matched, so the deletion must be spent right here, and there are exactly two ways to spend it. You never need to branch twice, which keeps the whole thing O(n) despite looking recursive.

**Where it shows up:** "valid palindrome after at most one deletion," and fuzzy-match problems where a bounded number of edits is allowed.

**Valid Palindrome II** — on first mismatch, return the OR of the two skips.
```cpp
while (l <= r){
    if (s[l] == s[r]){ l++; r--; continue; }

    // first mismatch --> spend the one deletion, two ways to do it
    else{
        return is_valid (s, l+1, r) || is_valid (s, l, r-1);
    }
}
return true; //since we have valid palindrome and hence we need to make zero deletions.
```

- **Time:** `O(n)` — n = string length; the one-deletion branch is only ever spent once.
- **Space:** `O(1)` — a few index variables, comparisons done in place.

---

## 6. Independent pointers, one per input

**What it is:** two pointers that aren't converging on a single array — each one walks its *own* input at its own pace, and you combine or pair across them.

**Why it's a distinct shape:** there's no "move the smaller" rule here, because the pointers aren't competing over the same space. Each advances according to its own sequence, which means the interesting part is always the **leftovers** — what to do once one input runs dry while the other still has elements.

**Where it shows up:** merging or interleaving two sequences, and greedy pairing across a sorted set.

**Merge Strings Alternately** — one pointer per word; interleave while both have characters, then drain each remainder separately.
```cpp
// Main loop: runs only while BOTH strings have characters left
while (p1 < m && p2 < n) {
    result.push_back(word1[p1++]);
    result.push_back(word2[p2++]);
}
// Leftover loops
while (p1 < m) { result.push_back(word1[p1++]); }
while (p2 < n) { result.push_back(word2[p2++]); }
```

- **Time:** `O(m+n)` — m, n = lengths of word1, word2; each character visited once.
- **Space:** `O(m+n)` — the result string holds every character from both inputs.

**Boats to Save People** — sort, then put pointers at both ends of the *same* array: pair the heaviest person with the lightest if they fit together, otherwise the heaviest sails alone. Twist is the greedy argument — the heaviest person needs a boat regardless, so the only question worth asking is whether anyone can ride along, and the lightest is the best candidate.
```cpp
sort(people.begin(), people.end());

while(l <= r){
    int weight = 0;
    int boat_count = 0;

    // 1st loop for adding heaviest people from right
    while(r > 0 && boat_count < 2 && weight + people[r] <= limit){
        weight += people[r]; boat_count++; r--;
    }
    // 2nd loop for adding lightest people from left
    while(l < n && boat_count < 2 && weight + people[l] <= limit){
        weight += people[l]; boat_count++; l++;
    }
    boats++;
}
```

- **Time:** `O(n log n)` — n = number of people; sort dominates the O(n) two-pointer scan.
- **Space:** `O(log n)` — sort's recursion stack; no extra array beyond the pointers.

---

*Threads out of this topic: 2 is the sorted-input mirror of Array Hashing — "complement lookup" — sorting gives you a direction to move, hashing gives you O(1) recall, and they solve the same pairing problem two different ways. 1's converging scan is what Linked Lists — "two pointers on a list" does with pointer speed instead of array indices.*
