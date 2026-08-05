# 2D Dynamic Programming

*Four sub-patterns, and the whole topic follows from one observation: a dp table gains a dimension exactly when the state has two moving parts. In 1D the state was "where am I." Here it's "where am I in string A **and** where am I in string B," or "which day **and** what did I do yesterday." Nothing else changes — same four-stage ladder, same base cases, same recurrence discipline. What does change is that two new bookkeeping problems appear, and both of them are pure index arithmetic rather than algorithm: the **+1 shift** that lets an empty prefix live at row 0, and the **offset** that lets a state legally be −1. Both trip people up far more often than the recurrences do. The load-bearing entry is pattern 1 — LCS is the template that three of these problems reduce to. Code blocks are main logic only.*

---

## 1. Two-sequence grid DP — the LCS template ⭐

**What it is:** a table where rows walk one string and columns walk the other, and `dp[i][j]` answers the question for the **prefixes** `A[0..i)` and `B[0..j)`. At every cell you ask one thing: do the current characters match? If yes, consume both and take the diagonal plus one. If no, you must drop a character from one side or the other, so you try both and take the better.

**Why the recurrence is forced rather than invented:** there are only three possible moves from a cell — up, left, or diagonal — and each one has a meaning. Diagonal means "both characters used." Up means "drop A's character." Left means "drop B's character." A match makes the diagonal strictly best, so you take it without comparing. A mismatch makes the diagonal illegal, leaving you to compare the other two. That's the entire derivation, and being able to give it in those terms is much stronger than reciting the formula.

**The index shift, which is the actual gotcha:** in the recursive version the base case is `index < 0 → return 0`. Arrays have no −1, so when you tabulate, **everything shifts by one** — the table is `(m+1) × (n+1)`, row 0 and column 0 mean "empty prefix," and character access becomes `text[index - 1]`. Your note calls this the new learning, and it is: the shift isn't a trick, it's the mechanical consequence of turning a negative base case into an array. It also comes for free — zero-initialising the table *is* the base case, so no separate filling loop is needed.

**Where it shows up:** longest common subsequence, edit distance, shortest common supersequence, distinct subsequences, wildcard and regex matching. Any question comparing two sequences where you're allowed to skip on either side.

**Longest Common Subsequence** — the memoised version first, where the base case is still readable as `index < 0`:
```cpp
// STEP 1: Base cases
if (index1 < 0 || index2 < 0) return 0;

if (dp_table[index1][index2] != -1) return dp_table[index1][index2];

// STEP 1,2: Base case + LOGIC --> MATCH
if (text1[index1] == text2[index2]){
    dp_table[index1][index2] = 1 + helper(index1- 1, index2 - 1, text1, text2, dp_table);
    return dp_table[index1][index2];
}

// STEP 2: LOGIC --> NOT MATCH --> split into 2 shifts
dp_table[index1][index2]  = 0 + max (helper(index1- 1, index2, text1, text2, dp_table),
                                    helper(index1, index2 - 1, text1, text2, dp_table) );

return dp_table[index1][index2];
```
And tabulated, with the shift applied — note `index - 1` on every character access:
```cpp
// already all 0s --> base case (row 0 / col 0 = empty string) is done
vector<vector<int>> dp_table (m + 1, vector<int>(n + 1, 0));

for (int index1 = 1; index1 < m + 1; index1++){
    for (int index2 = 1; index2 < n + 1; index2++){

        // MATCH
        if (text1[index1 - 1] == text2[index2 - 1]){
            dp_table[index1][index2] = 1 + dp_table[index1 - 1][index2 - 1];
        }

        // NOT MATCH
        else{
           dp_table[index1][index2]  = 0 + max (dp_table[index1 - 1][index2] ,
                                    dp_table[index1][index2 - 1]  );
        }
    }
}
return dp_table[m][n];
```

- **Time:** `O(m · n)` — m, n = the two string lengths; every cell filled once in `O(1)`.
- **Space:** `O(m · n)` — the full table (space-optimises to `O(n)` with two rows, since each row only reads the one above).

---

## 2. LCS as a subroutine — recognising the disguise

**What it is:** problems that are not phrased as "find the common subsequence" but reduce to it after one line of reasoning. You compute the LCS and then do arithmetic on it, or you feed LCS a cleverly chosen second string.

**Why this is worth its own slot:** the hard part of these is never the DP — it's noticing. Once you've written the LCS template, the return on recognising a disguised instance is enormous, because the implementation is already done. The two disguises below are the ones worth having memorised cold, since both reductions are a single sentence and both are common.

**Where it shows up:** delete operation for two strings, minimum ASCII delete sum, longest palindromic subsequence, minimum insertions to make a string palindromic, shortest common supersequence. If a problem is about two sequences and allows deletions, try LCS before anything else.

**Delete Operation for Two Strings** — everything not in the common subsequence has to go, from both sides. So the deletions are `(m − LCS) + (n − LCS)`, which is `m + n − 2·LCS`. That's the whole problem; the DP is a library call.
```cpp
int common_length = LCS(word1, word2);

// delete non-LCS chars from BOTH strings
return (word1.size() + word2.size() - (2 * common_length));
```

- **Time:** `O(m · n)` — m, n = the two word lengths; one LCS table.
- **Space:** `O(m · n)` — the LCS table.

**Longest Palindromic Subsequence** — the reduction is one line and genuinely delightful: a palindrome reads identically forwards and backwards, so **the longest palindromic subsequence of `s` is the longest common subsequence of `s` and `reverse(s)`.** Any subsequence appearing in both must read the same in both directions. No new code at all.
```cpp
// reverse s --> now LPS becomes LCS(s, reverse)
string r = s;
reverse(r.begin(), r.end());

return LCS(s, r);
```

- **Time:** `O(n²)` — n = string length; LCS of the string against itself reversed.
- **Space:** `O(n²)` — the LCS table.

---

## 3. Grid over "position × last choice"

**What it is:** the second dimension isn't another sequence — it's a small piece of **carried state**. `dp[day][last]` is the best score through `day`, given that the previous day's choice was `last`. The table is `n × 4` rather than `n × n`, because the state is drawn from a tiny fixed set.

**Why the constraint forces the second dimension:** "you can't repeat yesterday's activity" makes the value of today depend on a decision made yesterday, so a one-dimensional `dp[day]` doesn't carry enough information to be extended. Adding the last choice to the state is the standard fix, and the cost is a constant factor because the choice set is size 3. The mechanism worth stealing is the **sentinel**: `last = 3` means "no restriction," which serves double duty — it's the day-0 state where nothing is forbidden, and it's the answer cell, because the final day has no day-after to constrain. One extra column removes two special cases.

**Where it shows up:** ninja's training, "no two adjacent choices the same," paint-house style problems, and stock problems with a holding state (`dp[day][holding]`). The tell is a constraint that references the *previous* decision rather than the previous index.

**Ninja's Training** — `dp[day][last] = max over task ≠ last of (points[day][task] + dp[day-1][task])`.
```cpp
// dp[day][last] --> max points till this day, given last chosen task
vector<vector<int>> dp_table (n, vector<int>(4, 0));

// base --> day 0
// if last was X, we could only have chosen something else on day 0
dp_table[0][0] = max(points[0][1], points[0][2]);
dp_table[0][1] = max(points[0][0], points[0][2]);
dp_table[0][2] = max(points[0][0], points[0][1]);
dp_table[0][3] = max(points[0][0], max(points[0][1], points[0][2]));

// for every day
for (int day = 1; day < n; day++){

    // for every possible last chosen
    for (int last = 0; last < 4; last++){

        dp_table[day][last] = 0;

        // try every task that is NOT last
        for (int task = 0; task < 3; task++){

            if (task != last){
                // take this task today + best till yesterday ending with this task
                int current_prospect = points[day][task] + dp_table[day - 1][task];
                dp_table[day][last] = max(dp_table[day][last], current_prospect);
            }
        }
    }
}

// last = 3 --> no restriction on final day
return dp_table[n - 1][3];
```

- **Time:** `O(n)` — n = days; the `4 × 3` inner work is a constant 12 per day.
- **Space:** `O(n)` — the table (space-optimises to `O(1)`, since only the previous row is read).

---

## 4. Signed choices over a running total — the subset-sum shape

**What it is:** every element gets a `+` or a `−` (or equivalently, goes into one of two groups), and you count how many complete assignments hit a target. The state is `(index, running_sum)`.

**Why the running sum has to become a dimension:** the recursion is easy and correct — branch two ways per element, hit the base case when the array runs out. But it's `O(2ⁿ)`, and to memoise it you need the sum in the key, because the same index with a different accumulated sum is a genuinely different subproblem. And the moment the sum becomes an array index you hit the wall: **sums go negative, arrays don't.** The fix is the same species as LCS's +1 shift — add an offset. If the total of all elements is `S`, the sum ranges over `[−S, S]`, so you index by `sum + S` and size the dimension `2S + 1`. That's the lesson this problem exists to teach.

**The other route,** worth knowing because interviewers like it: split the elements into a positive group P and a negative group N. Then `P − N = target` and `P + N = total`, so `P = (target + total) / 2` — and the problem becomes "count subsets summing to a fixed value," which is plain subset-sum with a non-negative dimension and no offset needed. If `(target + total)` is odd or negative, the answer is 0 immediately.

**Where it shows up:** target sum, partition equal subset sum, count of subsets with a given sum, last stone weight II, and the 0/1 knapsack family generally.

**Target Sum** — the recursion is written and correct; **this one stops at stage 1.** Branch `+` and `−`, count the leaves that land on target.
```cpp
// 1. base --> finished array
if (index > nums.size() - 1){
    if (curr_sum == target) return 1;
    else return 0;
}

// 2. LOGIC --> + or -
int plus = helper(nums, target, curr_sum + nums[index], index + 1);
int subtract = helper(nums, target, curr_sum - nums[index], index + 1);

// 3. return --> total ways
return (plus + subtract);
```

- **Time:** `O(2ⁿ)` as written — n = array length; `O(n · S)` once memoised with the offset, S = total sum.
- **Space:** `O(n)` recursion stack as written; `O(n · S)` for the memo table.

*This is the honest gap in this topic: the memoised and tabulated stages don't exist yet, which means the offset lesson — the entire reason Target Sum is assigned — hasn't been written down. Finish this one before the others.*

---

*Threads out of this topic: **both index headaches here are the same headache.** LCS shifts by +1 because a base case of `index < 0` has to live somewhere in the array; Target Sum offsets by the total because a negative sum has to live somewhere too; and the LIS template in 1D DP shifts its `prev` column by +1 for exactly the same reason. When a state can legally be "before the beginning" or "below zero," you move the whole axis. Pattern 3's carried "last choice" is the same idea as LIS carrying `prev` — a decision that constrains the next one becomes a dimension.*

*Still open from your to-do: **grid DP** (unique paths, minimum path sum — the gentlest 2D problems and a good warm-up you've skipped), **coin change / coin change II** (unbounded knapsack), and **partition equal subset sum**, which is pattern 4 with the two-group reduction already applied.*
