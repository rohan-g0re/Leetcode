# Array Hashing

*Eight sub-patterns, and unlike the other topics this one is a single idea escalating in power: **precompute what you need to recognize.** A bare set → a value→index map → signed counts → keyed buckets → count buckets → parallel structures → prefix state. Read it as one arc rather than eight boxes; the load-bearing entry is **2**, the archetype every other one is a variation on. Code blocks are main logic only.*

---

## 1. Seen-set

**What it is:** the simplest hash — a set of "things I've already walked past," so a repeat is an O(1) hit.

**Why it beats the nested loop:** the naive answer compares every pair, which is O(n²). A set says "I don't need to compare against everything, I just need to remember everything," trading O(n) space for O(n) time. And because a duplicate can be reported the instant you find it, you usually exit long before the end.

**Where it shows up:** "are there any duplicates," "have I seen this before," visited-tracking in traversals. It's the floor of this whole topic — every pattern below is this with a richer payload than a plain bool.

**Contains Duplicate** — check membership, then insert.

```cpp
for (int x : nums){
    if (seen_numbers.find(x) != seen_numbers.end() ) { return true; }
    seen_numbers.insert(x);
}
return false;
```

- **Time:** `O(n)` — n = number of elements; one pass, each lookup O(1).
- **Space:** `O(n)` — the set can hold every element.

---

## 2. Complement lookup (value → index) ⭐

**What it is:** as you scan, you ask "have I already seen the number that *completes* this one?" Because the map stores `value → index`, the answer is one lookup.

**Why it's the canonical hash trick:** the brute force searches forward for a partner, which is O(n²). The flip is to stop searching forward and instead **record what you'd need to see**, so that when the partner shows up it recognizes *you*. Every element does one O(1) lookup and one O(1) insert, so the pass is linear. The detail that matters in practice: you store the **index**, not just the value, because the problem wants positions back — and you must look up *before* inserting, or an element whose complement is itself will match against its own entry.

**Where it shows up:** "two numbers that sum to target and I need their indices," and generally any "find two things that combine to X" on unsorted input. Compare it with Two Pointers — "fix one two-pointer the rest" — sorted input gives you a *direction to move* instead, so you can drop the map and use O(1) space. Two solutions, two different resources spent.

**Two Sum** — look up `target - nums[i]`, then insert.

```cpp
for (int i = 0; i < nums.size(); i++){
    int diff = target - nums[i];

    auto iterator = map.find(diff);
    if (iterator != map.end()){
        return {iterator->second, i};   // stored INDEX is what we return
    }

    map.insert({nums[i], i});   // insert AFTER the lookup
}
```

- **Time:** `O(n)` — n = number of elements; one pass, O(1) map lookup and insert each.
- **Space:** `O(n)` — map can store up to n value→index pairs.

---

## 3. Frequency counter + signed-cancel

**What it is:** count occurrences — but signed. Add for one string, subtract for the other, and if everything nets to zero the two matched exactly.

**Why the signed trick is neat:** one array does the job of two, and the comparison "are these the same multiset?" collapses into "is every count zero?" The practitioner's detail here is the `x - 'a'` offset: because the alphabet is fixed at 26, you can drop the hash map entirely for a plain array, which is both faster and genuinely O(1) space rather than O(n). **A bounded alphabet turns a map into an array — always check whether the input is bounded before reaching for a hash.**

**Where it shows up:** anagram checks, permutation tests, "same characters, same counts."

**Valid Anagram** — `++` over `s`, `--` over `t`, then assert all zero.

```cpp
if (s.size() != t.size()) return false;

vector <int> frequency (26, 0);
for (char x : s){ frequency [ x - 'a'] ++ ; }
for (char x : t){ frequency [ x - 'a'] -- ; }

for (int count : frequency){
    if (count != 0){ return false; }
}
return true;
```

- **Time:** `O(n)` — n = string length; two linear passes to fill and check counts.
- **Space:** `O(1)` — fixed 26-slot array, independent of input size.

---

## 4. Canonical key → bucket of originals

**What it is:** collapse each item to a **canonical form** — here, its sorted letters — and use that as a map key, so everything sharing a canonical form lands in the same bucket automatically.

**Why it groups for free:** anagrams differ only in ordering, so their sorted forms are byte-identical. That means the map itself does the grouping; you never compare two words against each other. The pattern generalizes well beyond anagrams — **any equivalence relation you can express as a normalization becomes a grouping problem the hash map solves for you.**

**Where it shows up:** "group things that are the same under some transformation" — anagrams, isomorphic strings, shifted sequences, shape-normalized coordinates.

**Group Anagrams** — sorted word is the key, the bucket holds the untouched originals.

```cpp
for (auto& string_i : strs){
    string sortedkey = string_i;
    sort(sortedkey.begin(), sortedkey.end());

    // this will make the key value pair as (aet, ate)
    map[sortedkey].push_back(string_i);
}

for (auto& pair : map){ result.push_back(pair.second); }
```

- **Time:** `O(n · k log k)` — n = number of words, k = max word length; sorting each word.
- **Space:** `O(n · k)` — map stores every word across all buckets.

---

## 5. Bucket by count (index as key)

**What it is:** to get the top-k frequent, you flip the map inside out — use the **frequency as an array index**, so `freq[3]` is the list of every element that appeared exactly 3 times. Then sweep from the high-frequency end and take k.

**Why it beats sorting the frequency map:** a frequency can never exceed `n`, so all possible frequencies fit in an array of size `n+1` — which means bucketing them is O(n), while sorting them would be O(n log n). You're exploiting a bound the problem handed you for free. **When the values you're sorting by are small integers with a known ceiling, bucket them instead of sorting them.**

**Where it shows up:** "top k frequent," "most common elements," and any ranking where a full sort is more than the question needs. A size-k heap (Heaps — "size-k heap") also solves it in O(n log k) — mention both and say the bucket version is O(n).

**Top K Frequent Elements** — count, scatter into `freq[count]`, sweep backward until you have k.

```cpp
for (int n : nums) { count[n] = 1 + count[n]; }

// ----------- IMPORTANT LOGIC ----------- 
for (const auto& entry : count) {
    freq[entry.second].push_back(entry.first);   // index = frequency
}

for (int i = freq.size() - 1; i > 0; --i) {      // sweep high freq --> low
    for (int n : freq[i]) {
        res.push_back(n);
        if (res.size() == k) { return res; }
    }
}
```

- **Time:** `O(n)` — n = number of elements; counting and bucketing are linear, beats O(n log k) heap.
- **Space:** `O(n)` — count map and frequency buckets hold up to n elements.

---

## 6. Several hash structures in parallel

**What it is:** validity depends on several independent constraints at once, so you run several hash structures side by side and update all of them in a single pass.

**Why parallel and not sequential:** scanning the board three separate times — once for rows, once for columns, once for boxes — is three times the work and three chances to write the same loop slightly wrong. Checking all three per cell catches a violation the instant it appears and lets you return immediately. The practitioner's detail worth remembering: the box key is a `pair`, and **`unordered_map` cannot hash a `pair` out of the box** — you either switch to an ordered `map` (as you did) or encode the box as a single int like `row/3 * 3 + col/3`.

**Where it shows up:** "no duplicates across rows AND columns AND boxes," multi-axis uniqueness, and constraint validation on grids.

**Valid Sudoku** — three structures, checked together, then all three updated.

```cpp
unordered_map<int, unordered_set<char>> rows;
unordered_map<int , unordered_set<char>> cols;
// IMPORTANT --> we need to use a map and not a unordered_map because --> IT DOES NOT SUPPORT PAIR AS A KEY 
map<pair<int, int>, unordered_set<char>> squares;

for (int row = 0; row < 9; row++){
    for (int col = 0; col < 9; col++){
        if (board[row][col] == '.') continue;

        pair <int, int> square_key = {row / 3, col / 3};

        // we find if we have duplicate in any of the 3 sets
        if (rows[row].find(board[row][col]) != rows[row].end() || 
            cols[col].find(board[row][col]) != cols[col].end() ||
            squares[square_key].find(board[row][col]) != squares[square_key].end()
        ) return false;

        // else we keep on inserting in all 3 sets
        rows[row].insert (board[row][col]);
        cols[col].insert(board[row][col]);
        squares[square_key].insert(board[row][col]);
    }
}
```

- **Time:** `O(1)` — board is fixed 81 cells, so the scan is constant work.
- **Space:** `O(1)` — rows, cols, squares track at most 81 fixed-size entries.

---

## 7. Prefix state: "seen so far" vs "total"

**What it is:** you carry two counts — everything **before** the current index (`prev`) and the **grand total** (`global`). At any element you then know both how many valid partners sit to your *left* (`prev[target]`) and how many sit to your *right* (`global[target] - prev[target]`), without ever looking right.

**Why it's a one-pass win:** counting triplets naively means picking a center and scanning both directions, which is O(n²). Precomputing the totals first means the right-hand count becomes a *subtraction*, so each center contributes `left × right` in O(1) and the whole thing runs in O(n). This is the same "running state vs total state" idea as a prefix sum, promoted from an integer to a hash map. **Anything you can't see yet, you can often compute as total minus seen.**

**Where it shows up:** "count triplets where the middle relates to the outer two," "how many valid elements on each side of me," subarray-sum-equals-k, and balanced-substring counting. The overflow detail is real: the counts multiply, so take the MOD *before* the multiplication, not after.

**Count Special Triplets** — totals first, then `prev` grows as you scan; right side is `global - prev`.

```cpp
// 1. global frequency map filling
for(int i = 0; i < n; i++){ global_freq[nums[i]]++; }

for(int i = 0; i < n; i++){
    prev_freq[nums[i]]++;              // seen-so-far grows as we advance
    long long target = 2 * nums[i];

    if(prev_freq.find(target) != prev_freq.end()){
        if(global_freq.find(target) != global_freq.end()){

            long long prev_count = prev_freq[target];
            long long next_count = global_freq[target] - prev_count;   // right = total - seen

            if(nums[i] == target) next_count = max(next_count - 1, 0LL);

            // --> we need to mod them before multiplication
            triplets += (prev_count % MOD) * (next_count % MOD);
        }
    }
}
```

- **Time:** `O(n)` — n = array length; two linear passes, no nested scan.
- **Space:** `O(n)` — global and prev frequency maps store up to n keys.

**Longest Balanced Subarray** — the honest brute force, kept for one reason: its **prune**. Once the remaining span can't possibly beat the best you've found, you stop. That early-exit habit is worth more than the problem.

```cpp
for (int j = i; j < n; j++){
    if (nums[j] % 2 == 0) even.insert(nums[j]);
    else odd.insert(nums[j]);

    if(odd.size() == even.size()){
        max_length = max (max_length, j - i + 1);
    }

// IMPORTANT --> we can also cut the upcoming loops --> if the max length has already reached the ceiling
    if (max_length > n - i) return max_length;
}
```

- **Time:** `O(n²)` — n = array length; nested loop tries every subarray start i and end j.
- **Space:** `O(n)` — even/odd sets can each hold up to n elements.

---

## 8. Length-prefix encoding

**What it is:** to pack a list of strings into one reversible string, prefix each with its length and a sentinel — `5#hello` — so the decoder never has to guess where a string ends.

**Why a plain delimiter fails:** any separator character you choose could legally appear *inside* one of the strings, and then decoding splits in the wrong place. A length prefix sidesteps the problem entirely: you read the number, then take exactly that many characters, and it doesn't matter what those characters are. **You're not marking the boundary, you're declaring the size — sentinels can be forged, lengths can't.**

**Where it shows up:** serialize/deserialize a collection, network framing, and any "encode these strings into one string" question. This is also the standard answer for why real protocols are length-prefixed rather than delimiter-separated.

**Encode & Decode Strings** — encode `len + "#" + str`, decode by reading to `#`, parsing the length, and jumping exactly that far.

```cpp
// ENCODE
for (auto& str : strs){
    encoded_string += to_string(str.size()) + "#" + str;
}

// DECODE
int i = 0;
while (i < s.size()) {
    int delimiter_pos = s.find('#', i);                        // find the sentinel
    int length = stoi(s.substr(i, delimiter_pos - i));         // parse the declared size

    int start = delimiter_pos + 1;
    result.push_back(s.substr(start, length));                 // take exactly that many

    i = start + length;   // Step 4: VERY IMPORTANT Move to next encoded string
}
```

- **Time:** `O(n)` — n = total characters across all strings; each char visited once to encode and decode.
- **Space:** `O(n)` — encoded string and result vector both hold all n characters.

---

*Thread out of this topic: **hash as O(1) memory** — every pattern here replaced a scan with a lookup, escalating from a bare bool (1) to full prefix state (7). Carry it into Sliding Window — "longest valid window + last-seen map", where the last-seen-index map is exactly pattern 2 with the stored index used to jump a pointer instead of to answer a query.*
