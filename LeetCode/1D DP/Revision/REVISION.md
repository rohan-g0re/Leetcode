# 1D Dynamic Programming

*Six sub-patterns, but before any of them there's one thing that matters more than all six: **the four-stage ladder.** Every DP problem you have solved was solved the same way — write the recursion, add a memo table, flip it into a bottom-up loop, then throw the table away and keep two variables. The recursion is where you think; the rest is mechanical. In an interview you say the recurrence out loud, write the memo version, and then say "and this tabulates, and the tabulation only ever looks back two steps so it space-optimises to O(1)" — that sentence is worth more than arriving at the optimal version directly, because it shows you know why it's optimal. The load-bearing entry is pattern 2, pick/not-pick, since it's the shape most subsequence problems reduce to. Code blocks are main logic only.*

---

## 1. The four-stage ladder

**What it is:** not a problem type — the process. Stage 1 is plain recursion, exponential and honest. Stage 2 adds a `dp` array checked at the top and written before every return, which collapses the exponential blowup because each state is now computed once. Stage 3 turns the recursion inside out: instead of asking downward from `n`, you fill upward from the base cases with a loop, which also kills the call stack. Stage 4 notices that the loop only ever reads `dp[i-1]` and `dp[i-2]`, so you keep two integers instead of an array.

**Why it's worth doing all four:** the jump from stage 1 to stage 2 is where the actual algorithmic win lives — `O(2ⁿ)` to `O(n)` — and it costs three lines. Stages 3 and 4 buy you constant factors and space, not complexity. Knowing which step buys what is the difference between reciting an optimisation and understanding it. The other reason: the base cases are easiest to get right in stage 1, where they're just `if` statements about the input, and they carry through the rest unchanged. Skip to stage 4 and you'll be guessing at what `prev2` should be initialised to.

**Where it shows up:** everywhere below. The problems in this pattern are the ones whose recurrence is a fixed look-back — `dp[i]` depends on `dp[i-1]`, `dp[i-2]`, maybe `dp[i-3]`, and nothing else.

**Climbing Stairs** — the ladder, all four rungs, on the simplest possible recurrence: `dp[i] = dp[i-1] + dp[i-2]`.

Stage 1, recursion:

```cpp
// 1. base case --> if reached at ending
if(stair == n) return 1;


// 2. logic
// if not there then we need to take 2 steps

int left = helper(stair + 1, n);

int right = 0;
if(stair < n - 1){
    right = helper(stair + 2, n);
}

return left + right;
```

Stage 2, memoization — three added lines, exponential to linear:

```cpp
// 1.1 if in table
if(dp[stair] != -1) return dp[stair];

// 1.2 if reached at ending
if(stair == n) return 1;

int left = helper(stair + 1, n, dp);

int right = 0;
if(stair < n - 1){
    right = helper(stair + 2, n, dp);
}

// 3. update and return
dp[stair] = left + right;
return dp[stair];
```

Stage 4, space-optimised tabulation — the array was only ever two cells wide:

```cpp
int prev = 1;
int prev2 = 1;

for(int i = 2; i <= n; i++){

    // fill the dp[i] using previous dp values
    int left = prev;
    int right = 0;
    if (i > 1) right = prev2;

    // calculate
    int curr = left + right;

    //updates:
    prev2 = prev;
    prev = curr;
}
return prev;
```

- **Time:** `O(2ⁿ)` recursion → `O(n)` memoised/tabulated — n = number of stairs.
- **Space:** `O(n)` memo or table → `O(1)` space-optimised — two integers.

**Min Cost Climbing Stairs** — same shape, cost added, and one thing that trips people at the end: you can finish from *either* of the last two steps, so the answer is `min(dp[n-1], dp[n-2])`, not `dp[n-1]`.

```cpp
dp[0] = cost[0];
dp[1] = cost[1];

for(int i = 2; i < n; i++){
    int one = cost[i] + dp[i-1]; // it may have come from '-1'th step
    int two = cost[i] + dp[i-2]; // it may have come from '-2'th step

    dp[i] = min(one, two);
}

// THE ONLY STEPS FROM WHICH WE COULD HAVE REACHED THE "PLATFORM" ABOVE
int last_step = dp[n-1];
int second_last_step = dp[n-2];

return min(last_step, second_last_step);
```

- **Time:** `O(n)` — n = number of steps; one pass.
- **Space:** `O(n)` tabulated → `O(1)` with two rolling variables.

**Frog Jump** — the same ladder with an absolute-difference cost. `dp[i] = min(dp[i-1] + |h[i]−h[i-1]|, dp[i-2] + |h[i]−h[i-2]|)`. The trailing comment on the space-optimised version is the kind of edge case worth keeping: with `n == 2` the loop body never runs, and the answer is already sitting in `prev1`.

```cpp
int prev2 = 0;
int prev1 = abs (height[1] - height[0]);

for (int i = 2; i < n; i++){

    int left = prev1+ abs(height[i-1] - height[i]);
    int right = prev2 + abs(height[i-2] - height[i]);
    current = min (left, right);

    prev2 = prev1;
    prev1 = current;
}

return prev1;

// submitting prev1 bcoz if n==2 --> it does not enter the loop --> and in that case we have anser in prev1
// also for normal cases it does not matter since "prev1 = current" at the end of every loop iteration
```

- **Time:** `O(n)` — n = number of stones; one pass, two candidates each.
- **Space:** `O(1)` — two rolling variables.

**N-th Tribonacci** — the same thing with a three-deep look-back, written straight at stage 4. The only reason it's interesting is as proof the ladder generalises: a `k`-deep recurrence space-optimises to `k` variables, and the shifting block at the bottom is the whole update.

```cpp
for(int i = 3; i <= n; i++){

    // 1. calculate current;

    current = zero + one + two;

    // 2. update values

    zero = one;
    one = two;
    two = current;
}
return two;
```

- **Time:** `O(n)` — n = the requested index.
- **Space:** `O(1)` — three rolling variables.

---

## 2. Pick / not-pick ⭐

**What it is:** at every index you face a binary choice. **Take** this element and jump back two, because taking it forbids its neighbour. **Skip** it and inherit whatever the previous index achieved. The answer is the better of the two.

**Why this one is load-bearing:** it's the smallest honest example of the decision framing that runs through all of DP — you're not computing a formula, you're enumerating choices and letting the recursion price them. It also generalises in a very specific direction: `dp[i] = max(take, skip)` becomes the skeleton for subset-sum, knapsack, and every "choose a subsequence under a constraint" problem, where "take" simply carries a different penalty. The practitioner's detail here is the base case for `index < 0`, which must return `0` — you land there by taking index 1 and jumping back two, and returning anything else silently corrupts the whole table.

**Where it shows up:** house robber and its variants, maximum sum of non-adjacent elements, delete-and-earn, and as the mental model for the knapsack family. The tell is a constraint of the form "you cannot use two things that are adjacent / conflicting."

**House Robber** — the recurrence stated plainly, at stage 4: `dp[i] = max(nums[i] + dp[i-2], dp[i-1])`.

```cpp
// prev1 = best over houses 0..i-1
// prev2 = best over houses 0..i-2 (empty prefix starts at 0)
int prev1 = nums[0];
int prev2 = 0;

// 2. logic --> for each house: TAKE or NOT TAKE
for (int i = 1; i < n; i++) {

    // TAKE --> rob this house + best from i-2 (cannot take adjacent)
    int take = nums[i] + prev2;

    // NOT TAKE --> skip this house --> keep best from i-1
    int skip = 0 + prev1;

    int best = max(take, skip);

    // 3. slide the window (space opt updates)
    prev2 = prev1;
    prev1 = best;
}
```

- **Time:** `O(n)` — n = number of houses; one pass, two candidates each.
- **Space:** `O(1)` — two rolling variables.

**Maximum Sum of Non-Adjacent Elements** — your own template file, the same recurrence written with the recursion still visible. Worth keeping the stage-1 version in your head, because the `index < 0` base case is only obvious here.

```cpp
// STEP 1. base case

if (index == 0) return arr[index];

if (index < 0) return 0; //out of bounds - reached here because we picked index 1 -- and then did n-2


// STEP 2: LOGIC & Recurive calls --> PICK & NOT PICK

int pick = arr[index] + helper(index - 2, arr);

int not_pick = 0 + helper(index - 1, arr);


// STEP 3: We have to choose the choice of max

return max(pick, not_pick);
```

*One fix to make: the memoised version of this template uses `if (dp[index] != 0)` as its "not computed yet" check. Zero is a legitimate answer, so that sentinel can't distinguish "empty" from "computed to 0." Use `-1`, as you do in every other file.*

- **Time:** `O(2ⁿ)` recursion → `O(n)` memoised — n = array length.
- **Space:** `O(n)` memo plus recursion stack → `O(1)` space-optimised.

**House Robber II** — the circular twist, and the resolution is the pattern worth remembering. First and last house are now adjacent, so they can't both be taken. Rather than complicate the recurrence, you **run the linear solver twice on two brackets** — once excluding the last house, once excluding the first — and take the max. Every valid circular selection omits at least one of the two ends, so one of the brackets always contains it.

```cpp
// BRACKET 1 --> exclude last house
vector<int> temp1 (nums.begin(), nums.end() - 1);

// BRACKET 2 --> exclude first house
vector<int> temp2 (nums.begin() + 1, nums.end());

// spawn House Robber 1 on both parts
int option1 = helper(temp1);
int option2 = helper(temp2);

return max(option1, option2);
```

- **Time:** `O(n)` — n = houses; two linear passes.
- **Space:** `O(n)` — the two sliced copies (`O(1)` if you pass index ranges instead).

---

## 3. Best ending here — the Kadane family

**What it is:** a single scan carrying a running "best subarray that ends exactly at this index." At each step you either extend the previous run or start fresh from the current element, and a separate global tracks the best you've ever seen.

**Why the two variables are genuinely different:** `curr` answers "best ending *here*," which is a constrained question with a local recurrence. `global_max` answers "best *anywhere*," which is just a max over all the local answers. Conflating them is the classic bug. The reason the recurrence works at all is that a prefix with negative sum can never help — dragging it along strictly reduces whatever follows — so the moment your running sum goes negative you drop it. That single observation is the whole algorithm.

**Where it shows up:** maximum subarray, maximum product, best time to buy and sell, longest run satisfying a property. The tell is "contiguous" — subarrays get this, subsequences get pattern 2.

**Maximum Subarray** — Kadane's, in the reset-on-negative spelling. No `dp` array at all; the accumulator *is* the table.

```cpp
for (int num : nums) {

    curr_sum += num;

    if (curr_sum > global_max) {
        global_max = curr_sum;
    }

    if (curr_sum < 0) {
        curr_sum = 0;
    }
}
```

- **Time:** `O(n)` — n = array length; brute force with three nested loops is `O(n³)`.
- **Space:** `O(1)` — two integers.

**Maximum Product Subarray** — the twist that makes this its own problem: for products you must also track the **minimum**, because one negative number turns the smallest product into the largest. So there are three candidates each step, not two, and you maintain two rolling values. This is worth being able to explain in one sentence — "a negative flips min and max, so I carry both" — because that sentence is the entire interview answer.

```cpp
for (int i = 1; i < n; i++){

    // there are 3 candidates:
    int cand1 = nums[i];
    int cand2 = nums[i] * prev_max_prod;
    int cand3 = nums[i] * prev_min_prod;

    // logic to update tables
    int curr_max_prod = max(cand1, max(cand2, cand3));
    int curr_min_prod = min(cand1, min(cand2, cand3));

    if (curr_max_prod > global_max){
        global_max = curr_max_prod;
    }

    prev_max_prod = curr_max_prod;
    prev_min_prod = curr_min_prod;
}
```

- **Time:** `O(n)` — n = array length; one pass, three candidates each.
- **Space:** `O(1)` — two rolling products plus the global (the `O(n)` tabulated version keeps two full arrays).

---

## 4. Best ending at i, found by scanning back — LIS

**What it is:** `dp[i]` is the best answer for a subsequence **ending exactly at i**, and to compute it you scan every earlier index `j`, keep the ones that are compatible, and take the best of `dp[j] + 1`. Quadratic, but complete.

**Why the "ending at i" definition matters so much:** the tempting definition is "LIS of the prefix `0..i`," and it doesn't work — it gives you no way to extend, because you don't know what the last element was. Pinning `dp[i]` to end at `i` makes the compatibility test a single comparison against `nums[i]`. The price is that the answer isn't `dp[n-1]`; the longest subsequence can end anywhere, so the answer is `max(dp[])`. Getting that pair right — restrictive definition, global max at the end — is the whole pattern.

**Where it shows up:** longest increasing subsequence, longest chain of pairs, Russian doll envelopes, largest divisible subset, and the "maximum number of non-overlapping things" family. Also worth knowing: LIS has an `O(n log k)` patience-sorting solution with binary search, so if the interviewer says "can you do better than n squared," that's the door.

**Longest Increasing Subsequence** — the `O(n²)` scan-back. Every cell starts at 1 because a single element is a valid subsequence of length 1.

```cpp
// dp[i] --> LIS length ENDING at index i (nums[i] is included as last element)
vector<int> dp(n, 1);
int result = 1; // at least single element

for (int i = 1; i < n; i++){

    // build best LIS that ENDS at i --> by trying every previous ending j
    for(int j = 0; j < i; j++){

        // only valid if strictly increasing
        if (nums[j] < nums[i]){
            // dp[i]  --> current best ending at i
            // dp[j] + 1 --> best ending at j, then append nums[i]
            dp[i] = max(dp[i], dp[j] + 1);
        }
    }

    // LIS can end anywhere --> track global max across all endings
    result = max(result, dp[i]);
}
```

- **Time:** `O(n²)` — n = array length; every pair `(j, i)` with `j < i` is tested.
- **Space:** `O(n)` — one dp array.

**LIS, pick/not-pick formulation** — the same problem expressed as pattern 2 with an extra piece of state: the index you last picked. This is the version that generalises, because the `prev` slot can carry any constraint. Note the offset — `prev` can be `-1`, and arrays can't be indexed at −1, so the column is `prev + 1` and the table needs `n+1` columns. Note also that **not-pick is unconditional**: your example says why, since picking a valid-but-large element (the 10 in `1, 10, 2, 3, 4, 5`) legally extends the run and ruins everything after it.

```cpp
// 2.1 pick --> ONLY IF valid wrt prev

int pick = 0;

if (prev == -1 || nums[index] > nums[prev]){

    // new prev becomes current index --> because we picked it
    pick = 1 + LIS(nums, index+1, index, dp_table);

}

// 2.2 not pick whatsoever --> prev stays the same

int not_pick = 0 + LIS(nums, index+1, prev, dp_table);


// 3. store + return --> best from this state
dp_table[index][prev + 1] = max(pick, not_pick);
```

- **Time:** `O(n²)` — n = array length; `n × (n+1)` distinct states, each `O(1)`.
- **Space:** `O(n²)` — the 2D memo table, plus `O(n)` recursion stack.

---

## 5. Suffix DP driven by a dictionary

**What it is:** `dp[i]` answers a question about the **suffix starting at i**, and the transition isn't a fixed offset — you try every word in a dictionary, and any word that matches at position `i` sends you to `dp[i + word.size()]`.

**Why you fill it backwards:** the answer at `i` depends on answers at positions *after* `i`, so those have to exist first. Filling front-to-back would ask about the future. The base case is the elegant part: `dp[n] = true`, because an empty suffix is trivially breakable — and that single `true` at the end is what every successful chain of words eventually lands on. Your comment about "patching True" to reach index `n` is exactly the right mental picture.

**Where it shows up:** word break, word break II, palindrome partitioning, decode ways, and any "can this string be split into valid pieces" question. The distinguishing feature is that the transition length is data-dependent rather than fixed, which is why the inner loop is over a dictionary rather than over `i-1, i-2`.

**Word Break** — backward fill, dictionary as the transition set.

```cpp
// dp[i] --> can we break s[i .. end] ?
vector<bool> dp(n + 1, false);

// n+1 because if we reach n+1th index by "PATCHING True" then it means that we have constructed the complete string --> hence we have INITIALIZED last index as true below

// 1. base case --> empty suffix is always breakable
dp[n] = true;

// 2. fill from the END backwards
for (int i = n - 1; i >= 0; i--) {

    // try EVERY word at this starting position
    for (string& word : wordDict) {

        int len = word.size();

        // word must fit && substring starting at i matches word
        if (i + len <= n && s.substr(i, len) == word) {

            // MAIN LOGIC --> if suffix AFTER this word is breakable --> then i is breakable
            if (dp[i + len] == true) {
                dp[i] = true;
                break; // found one valid word --> no need to try more
            }
        }
    }
}

// 3. return --> can we break from index 0 ?
return dp[0];
```

- **Time:** `O(n · w · L)` — n = string length, w = dictionary size, L = max word length (the `substr` compare).
- **Space:** `O(n)` — the boolean dp array.

---

## 6. Lives in the DP folder, isn't DP

**What it is:** two problems whose final solutions are not dynamic programming at all. Keeping them straight matters, because calling something DP when it has no memoised subproblems is the kind of thing an interviewer will pick at.

**Longest Palindromic Substring** — your DP attempts (recursion, then a 2D memo of substrings) both die, one to time and one to memory. The solution you kept is **expand around centre**: treat every index as a possible middle and grow outward while the characters match. The reframing is the insight, and it's stated in your notes — stop validating palindromes from the outside in, start from the centre and ask how far it reaches. The detail that catches people is that you need **two expansions per index**, because an even-length palindrome has no single character at its centre. It's `O(n²)` time like the DP table, but `O(1)` space, which is why it wins.

```cpp
// IMNPORTANT --> the for loop is helpful such that it lets us TEST every element as the CENTER OF THE PALINDROMIC STRING

for (int i = 0; i < n; i++){

    // IF the chosen S[i] IS THE CENTER OF "ODD-LENGTH" PALINDROME - then l and r can be initilaized as a single element

    int l = i;
    int r = i;

    while(l >= 0 && r < n && s[l] == s[r]){
        // the while statement makes sure that the current string is palindrome

        if (r - l + 1 > global_max){
            result = s.substr(l, r-l+1);
            global_max = r-l+1;
        }

        l--;
        r++;
    }

    // IF S[i] IS THE CENTER OF "EVEN-LENGTH" PALINDROME - then l and r CANNOT be initilaized as a same element --> and hence we need to have two different elements as the center

    l = i;
    r = i+1;

    while(l >= 0 && r < n && s[l] == s[r]){

        if (r - l + 1 > global_max){
            result = s.substr(l,r-l+1);
            global_max = r-l+1;
        }

        l--;
        r++;
    }
}
```

- **Time:** `O(n²)` — n = string length; n centres, each expanding up to n.
- **Space:** `O(1)` — two pointers (excluding the returned substring).

**Generate Parentheses** — **pure backtracking, no DP.** There's no table and no reused subproblem; you're enumerating every valid string by building it character by character and pruning branches that can't be legal. The state that makes the pruning work is `open_count`, and your note records exactly why a boolean flag failed: a flag can only say "something is open," but you need to know *how many*, because closing one when three are open doesn't make the string complete.

```cpp
// 1. base case --> opening and closing zero --> push in result

if(opening == 0 && closing == 0){
    result.push_back(str);
    return;
}

// 2. if opening available --> add that thing --> increment open_count

if(opening > 0){
    recurse(opening - 1, closing, open_count + 1, str + '(', result);
}

// 3. if open_count > 0 && closing available --> add that thing --> decrement open_count

if (open_count > 0 && closing > 0){
    recurse(opening, closing - 1, open_count - 1, str + ')', result);
}
```

- **Time:** `O(4ⁿ / √n)` — n = pairs; the count of valid strings (the nth Catalan number), each built in `O(n)`.
- **Space:** `O(n)` — recursion depth; output excluded.

---

*Threads out of this topic: the **four-stage ladder** of pattern 1 is the thing to carry into every DP problem you meet — recursion, memo, tabulate, shrink. Pattern 2's take-or-skip framing is the direct ancestor of the knapsack and subset-sum problems in 2D DP, where "take" costs capacity instead of an adjacent slot. Pattern 4's `prev`-carrying LIS formulation is a 1D problem that needed a 2D table, which is the natural bridge into two-sequence DP — once the state has two moving parts, the table gains a dimension.*

*Still open from your to-do: **coin change** and **coin change II** (unbounded knapsack — the same take/skip, but taking doesn't advance the index), and **partition equal subset sum** (subset-sum, which is pick/not-pick with a running total as the second dimension).*
