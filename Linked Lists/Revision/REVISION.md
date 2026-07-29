# Linked Lists

*Six sub-patterns, but really two skills: **not losing the rest of the list** (1, 2) and **making structure appear out of pointer motion** (3, 6). The other two are escape hatches — a hash map when the links are arbitrary, and a vector when the pointer work isn't worth the bug risk. Code blocks are main logic only.*

---

## 1. Dummy node

**What it is:** you allocate one throwaway node in front of the list, build onto `dummy->next`, and return that at the end.

**Why it removes bugs:** without it, the very first insertion is a special case — there's no previous node to attach to, so you need separate code for "is this the head?" every single time. The dummy gives *every* node a predecessor, so one loop body handles all of them and the head being null or changing stops mattering. **One line to carry: the dummy exists so the head stops being a special case.**

**Where it shows up:** any time you're *building* a new list rather than walking one — merging, adding, filtering, or the heap-driven merge from Heaps — "Front line of k sorted lists". If you find yourself writing `if (result == nullptr) result = node; else tail->next = node;`, you wanted a dummy.

**Add Two Numbers** — dummy plus carry, one pass over both lists. Twist is the `if(l1)`/`if(l2)` guards so a shorter list quietly contributes 0, and a leftover carry becomes its own final node.
```cpp
ListNode* dummy_node = new ListNode(-1); // we are going to its NEXT later
ListNode* mover = dummy_node;
int carry = 0;

while(l1 != nullptr || l2 != nullptr){ // both of them should finish for the loop to end
    int sum = 0;
    if(l1) sum += l1 -> val;
    if(l2) sum += l2 -> val;
    sum += carry;

    ListNode* temp = new ListNode(sum%10);
    mover -> next = temp;
    mover = mover -> next;
    carry = sum / 10;

    if (l1) l1 = l1 -> next; // we dont want to shift it if it is already on a nullptr
    if (l2) l2 = l2 -> next;
}

if (carry > 0){ mover -> next = new ListNode(carry); }
return dummy_node -> next;   // the real head
```

- **Time:** `O(n+m)` — n, m = lengths of l1, l2; single pass over both.
- **Space:** `O(max(n,m))` — new nodes for the output list, no other structures.

**Merge Two Sorted Lists** — your variant skips the sentinel and instead *elects* the smaller head as the dummy, then splices. Twist is the O(1) tail-attach at the end: whichever list still has nodes is already sorted, so you link it wholesale instead of looping.
```cpp
// elect the smaller head as the dummy
if (list1 -> val <= list2->val){ dummy_node = list1; l1 = list1 -> next; l2 = list2; }
else{ dummy_node = list2; l2 = list2 -> next; l1 = list1; }
ListNode* temp = dummy_node;

while (l1 != nullptr && l2 != nullptr){
    if (l1 -> val <= l2 -> val){ temp -> next = l1; l1 = l1-> next; }
    else{ temp -> next = l2; l2 = l2 -> next; }
    temp = temp -> next;
}

// one of the lists might be remaning --> attach it wholesale
if (l1 != nullptr){ temp -> next = l1; }
else{ temp -> next = l2; }
```

- **Time:** `O(n+m)` — n, m = lengths of list1, list2; single merge pass.
- **Space:** `O(1)` — reuses existing nodes, only pointer variables.

---

## 2. Link reversal (prev / curr / front)

**What it is:** the three-pointer dance. Stash `front = curr->next`, flip `curr->next = prev`, then slide `prev` and `curr` forward one step.

**Why you memorize it cold:** reversing in place costs O(1) space, and a surprising number of "hard" list problems are just this move applied to a sub-range. The single rule that makes it work — and the single reason people's code explodes — is **stash `front` before you overwrite the link**, because the moment you write `curr->next = prev` the rest of the list is unreachable unless you saved it.

**Where it shows up:** reverse the whole list, reverse a chunk, reorder, palindrome checks. When an interviewer says "in place, O(1) space" about a list, this is almost always the move they're fishing for.

**Reverse Linked List** — the base dance. The four commented steps are the thing to remember.
```cpp
ListNode* prev = nullptr;
ListNode* mover = head;

while(mover != nullptr){
    // 1. store front which is basically the next node in original Linked List
    ListNode* front = mover -> next;
    // 2. change direction of link for the current node in reverse direction
    mover -> next = prev;
    // 3. update prev by incrementing it to mover
    prev = mover;
    // 4. update mover to front
    mover = front;
}
return prev; // mover is on nullptr --> hence the head of this LL will be on prev
```

- **Time:** `O(n)` — n = number of nodes; single pass, each node visited once.
- **Space:** `O(1)` — only pointer variables, reversed in place, no extra list allocated.

**Reverse Linked List II** — reverse only `[left, right]`. Twist is the three-phase bookkeeping: walk to `left`, run the dance exactly `right-left+1` times, then **relink both seams** — and handle `left == 1`, where there is no left chain and the new head is `prev`.
```cpp
// PHASE 1 --> walk to left, remember the seam
if(left != 1){
    for(int i = 1; i < left - 1; i++){ mover = mover -> next; }
    left_chain_dummy = mover;
    switch_dummy = mover -> next;
}

// PHASE 2 --> the dance, exactly (right - left + 1) times
int total_nodes = right - left + 1;
ListNode* prev = nullptr;
mover = switch_dummy;
while(total_nodes > 0){
    ListNode* front = mover -> next;
    mover -> next = prev;
    prev = mover;
    mover = front;
    total_nodes--;
}

// PHASE 3 --> relink both seams
switch_dummy -> next = mover; // reversed tail --> [right+1, end]

if (left_chain_dummy != nullptr){ // because left can be 1 in which case we dont need to link dummy chain
    left_chain_dummy-> next = prev;
    return head;
}
return prev;   // left == 1 --> new head is prev
```

- **Time:** `O(n)` — n = number of nodes; walk to `left` plus a bounded reversal pass.
- **Space:** `O(1)` — only pointer variables, reversed in place.

---

## 3. Two pointers on a list

**What it is:** two pointers moving at different speeds, or holding a fixed gap, so that structure falls out of their relative motion.

**Why it beats counting:** you avoid a length pre-pass by letting the geometry do the counting for you — **the gap *is* the count.** Fast/slow (Floyd) finds cycles and midpoints because a faster pointer inside a loop must eventually lap a slower one; a k-gap pair finds "nth from end" because when the leader hits null, the follower is sitting exactly n from the tail.

**Where it shows up:** cycle detection, finding the middle, "nth node from the end," and any regroup-by-position problem. If a solution starts with "first, count the length," ask whether two pointers could have skipped that pass.

**Odd Even Linked List** — two in-place chains each hopping two nodes, then stitched. Twist is saving `even_head` *before* you start weaving, because you'll need it after the loop has destroyed the original ordering.
```cpp
ListNode* odd = head;
ListNode* even = head -> next;
ListNode* even_head = head -> next;   // save it BEFORE weaving

while(even != nullptr && even -> next != nullptr){
    odd -> next = odd -> next -> next;
    even -> next = even -> next -> next;
    // it is the next location because we changed the links now
    odd = odd -> next;
    even = even -> next;
}
odd -> next = even_head;   // link both the chains
```

- **Time:** `O(n)` — n = number of nodes; single pass weaving odd/even chains.
- **Space:** `O(1)` — only pointer variables, no extra list allocated.

**Remove Nth Node From End** — your version does a length pre-pass and deletes at `len - n + 1`. Twist is the null-guard before `mover->next->next`, so deleting the *tail* doesn't dereference null, plus the separate head-deletion case.
```cpp
int target_node = len - n + 1;  // "+1" since without it -> deleting head is difficult in a Linked List

if (target_node == 1){ head = head -> next; delete(mover); return head; }

target_node--; // stop at the node BEFORE the target
while(target_node > 0){
    target_node--;
    if (target_node == 0){
        if (mover -> next -> next) mover -> next = mover -> next -> next;
        else mover -> next = nullptr; // deleting the tail --> ELSE we access null's next
        return head;
    }
    mover = mover -> next;
}
```

- **Time:** `O(n)` — n = number of nodes; one pass for length, one pass to the target.
- **Space:** `O(1)` — only pointer variables.

**Linked List Cycle** — your destructive shortcut: stamp each visited node's value with `INT_MAX`, and re-seeing that stamp means a cycle. Twist worth stating honestly — **it mutates the input**, which is usually disqualifying; Floyd's fast/slow is the non-destructive answer and the one to lead with in an interview.
```cpp
while(head != nullptr){
    if (head -> val == INT_MAX) return true;
    else{
        head -> val = INT_MAX;
        head = head -> next;
    }
}
return false;
```

- **Time:** `O(n)` — n = number of nodes; each node visited once before its stamp is seen.
- **Space:** `O(1)` — mutates node values in place instead of a set; Floyd's fast/slow is the non-destructive O(1)-space alternative.

---

## 4. Hash map of node pointers

**What it is:** when a node points somewhere arbitrary — a `random` pointer that can hit any node — a map from **old node → new node** lets you clone the structure without understanding its shape.

**Why two passes:** on the first pass you can't wire anything, because the node a `random` points to may not exist yet. So pass 1 creates every clone and records the mapping; pass 2 wires `next` and `random` by asking the map "where did the thing this used to point at end up?" **The map is a translation table from old addresses to new ones.**

**Where it shows up:** deep-copying a graph or a list with cross-links, and any "rebuild this structure with new objects but identical topology" problem.

**Copy List with Random Pointer** — pass 1 builds nodes and the map, pass 2 wires both pointers through lookups.
```cpp
// PASS 1 --> clone every node, record old --> new
while(mover != nullptr){
    Node* temp = new Node (mover->val);
    mp[mover] = temp;
    mover = mover -> next;
}

// PASS 2 --> wire next AND random via lookups
mover = head;
while(mover != nullptr){
    Node* copy = mp[mover];
    copy -> next = mp[mover -> next];
    copy -> random = mp[mover -> random];
    mover = mover -> next;
}
return mp[head];
```

- **Time:** `O(n)` — n = number of nodes; two linear passes to clone and wire.
- **Space:** `O(n)` — hash map from old to new nodes; an O(1)-space interleave-clone variant exists but isn't used here.

---

## 5. Escape hatch: copy values into a vector

**What it is:** when the pointer gymnastics get hairy, dump the values into an array, solve the problem there with easy random access, and write the answers back into the nodes.

**Why it's legitimate:** you trade O(n) space for a large drop in bug surface — indices forgive mistakes that next-pointers do not. The honest framing matters: **this is the pragmatic fallback, not the optimal**, and saying so yourself ("I'd do this first for correctness, then tighten to the O(1)-space reversal if we need it") reads as judgment rather than ignorance.

**Where it shows up:** reorder, palindrome, or anything that wants random access into a structure that only offers forward links.

**Reorder List** — copy values to a vector, then two pointers (`l` from the front, `r` from the back) overwrite node values in the `L0, Ln, L1, Ln-1…` weave. Twist: no relinking whatsoever — you only rewrite `val`.
```cpp
// dump values
while (temp != nullptr){ copy_ll.push_back(temp -> val); temp = temp -> next; }

// two pointers over the vector, overwrite node values in place
int l = 0;
int r = copy_ll.size() - 1;
int node_number = 1;
temp = head;

while(temp != nullptr){
    if (node_number % 2 != 0){ //odd node gets left side value
        temp -> val = copy_ll[l];
        l++;
    }
    else{
        temp -> val = copy_ll[r];
        r--;
    }
    node_number++;
    temp = temp -> next;
}
```

- **Time:** `O(n)` — n = number of nodes; one pass to copy, one pass to overwrite values.
- **Space:** `O(n)` — vector holds all node values, the escape-hatch tradeoff for correctness.

---

## 6. Indexes as pointers (Floyd on an array)

**What it is:** an array where `next = nums[i]` *is* a linked list in disguise — values point at indices. A duplicate value means two arrows land on the same node, which is exactly a **cycle**, and Floyd's algorithm finds its entrance.

**Why it's the clever answer:** it locates the duplicate in O(n) time and O(1) space without sorting, without a set, and without modifying the array — hitting all three constraints the problem deliberately imposes. **The reframe is the whole insight: stop seeing an array, start seeing a list.**

**Where it shows up:** "n+1 values in the range [1,n], find the duplicate, don't modify the input, O(1) space." The constraints are the tell — they exist specifically to rule out every easier approach.

**Find the Duplicate Number** — this is the rare case where **your coded logic is not the pattern named above**. What you wrote is binary search on the *value space* (count how many elements are `<= mid`; the count overshoots on the side containing the duplicate) — a direct cousin of Binary Search — "Binary search on the answer space".
```cpp
int start = 1;
int end = nums.size() - 1;

while(start < end){
    int mid = start + (end - start) / 2;

    int cnt = 0;
    for(int num: nums){ if(num <= mid) cnt++; }

    if (cnt <= mid) start = mid + 1;   // duplicate lives in the upper half
    else end = mid;                     // duplicate lives in [start, mid]
}
// we can return start --OR-- end because they are in the same position
return start;
```

- **Time:** `O(n log M)` — M = value range [1,n]; binary search on value with an O(n) count each step.
- **Space:** `O(1)` — only loop counters; Floyd's cycle detection solves it in O(n) time, O(1) space.

*Know both: lead with Floyd (O(n), O(1)) as the headline answer, and keep this BS version as the easy-to-derive backup. Note the `start < end` / `end = mid` shape — identical to Find Pivot in Binary Search — "Rotated/pivot search".*

---

*Threads out of this topic: pattern 1's dummy node is the same build loop the heap drives in Heaps — "Front line of k sorted lists"; pattern 6's binary search is Binary Search — "Binary search on the answer space" wearing a different costume; and pattern 3's two-pointer motion is the list-shaped version of everything in Two Pointers.*
