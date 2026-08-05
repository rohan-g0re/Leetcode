# Stacks

*Four sub-patterns. The load-bearing one is **pattern 1 — the monotonic stack**; the other three are the stack used as a simulator, a merger, and a design primitive. Code blocks are main logic only.*

---

## 1. Monotonic stack (Next Greater Element) ⭐

**What it is:** you keep a stack whose values stay in strict order (here, decreasing from bottom to top). When a new element arrives you pop everything it beats — and for those popped elements, *this new element is their answer*. **Why it's clever:** each element is pushed and popped at most once, so "for each element find the next greater/warmer" collapses from O(n²) to O(n). The stack is a running memory of "things still waiting for their answer." **Trigger:** "next greater / next warmer / next smaller," or spans — anything where each element waits for the first later element that beats it.

**Daily Temperatures** — the canonical NGE. Twist over the textbook version: you need the *distance*, so you push **indices, not values**, and answer with `top - i`.
```cpp
stack<int> st;   // store INDEX, not temperature

for (int i = n-1; i >= 0; i--) {
    if (st.empty()) {
        ngeResult[i] = 0;
        st.push(i);            // push index
    }
    else {
        // pop until we find a hotter day
        while (!st.empty() && temperatures[st.top()] <= temperatures[i]) {
            st.pop();
        }
        if (st.empty()) { ngeResult[i] = 0; }
        else { ngeResult[i] = st.top() - i; }
        st.push(i);
    }
}
```

- **Time:** `O(n)` — n = number of days; each index is pushed and popped at most once.
- **Space:** `O(n)` — worst case (strictly decreasing temps) the stack holds all n indices.
*(Your first NGE draft pushed values instead of indices and returned the value, not the gap — this index version is the one to remember.)*

**Online Stock Span** — same monotonic stack but *streaming*: you can't look ahead, so you look **back**, squashing already-computed spans into the stack as `{price, span}` pairs so you never re-walk them.
```cpp
int span = 1;
if (price_stack.empty() || price_stack.top() > price) {
    price_stack.push({price, 1});
}
else{
    while(!price_stack.empty() && price_stack.top().first <= price){
        span += price_stack.top().second;   // absorb the popped element's span
        price_stack.pop();
    }
    price_stack.push({price, span});
}
return span;
```

- **Time:** `O(1)` amortized — n = number of prices; each price is pushed and popped once across all calls.
- **Space:** `O(n)` — n = number of days recorded; stack holds unmerged price/span pairs.

---

## 2. Stack as simulator / history

**What it is:** the stack *is* the state of an ongoing process — the last thing you did sits on top, ready to be undone, doubled, matched, or combined. **Why a stack fits:** these problems have LIFO structure baked in — the most recent open bracket is the first to close, the most recent number is the first to cancel. Any time "the thing I care about is the most recent unresolved one," reach for a stack. **Trigger:** brackets, expression evaluation, undo/history, nested decoding, collisions.

**Valid Parentheses** — push opens, on a close check the top matches. Two twists = the two failure modes: stack **empty** on a close (extra closer), stack **non-empty** at the end (unmatched opener).
```cpp
for (char bracket : s){
    if ( bracket == '(' || bracket == '{' || bracket == '['){
        stack.push(bracket);
    }
    else{
        if ( stack.empty() || map[bracket] != stack.top()) return false; // mismatch OR too many closers
        stack.pop();
    }
}
if (stack.size() == 0) return true;   // leftover openers => invalid
return false;
```

- **Time:** `O(n)` — n = length of s; each character is processed once.
- **Space:** `O(n)` — worst case every character is an opener stored on the stack.

**Evaluate Postfix (RPN)** — pop two, apply, push. Twist is **operand order**: `b` pops first but is the *right* operand, so `a - b` and `a / b` must respect it.
```cpp
// the naming is to represent the order in the arithmetic --> "a" should be before "b" in equations
int b = stack.top(); stack.pop();
int a = stack.top(); stack.pop();

if (s == "+"){ stack.push(a + b); }
else if (s == "-"){ stack.push(a - b); }
else if (s == "*"){ stack.push(a * b); }
else if (s == "/"){ stack.push(a / b); }
```

- **Time:** `O(n)` — n = number of tokens; each token is pushed or popped once.
- **Space:** `O(n)` — worst case all operands sit on the stack before an operator.

**Baseball Game** — pure simulation. Twist: `+` must not lose the top it read, so stash and push it back.
```cpp
if (ele == "C"){ st.pop(); }
else if(ele == "D"){ st.push(st.top() * 2); }
else if(ele == "+"){
    int sum = st.top();
    int temp = sum;
    st.pop();
    sum += st.top();
    st.push(temp);   // put back the one we peeked
    st.push(sum);
}
else{ st.push(stoi(ele)); }
```

- **Time:** `O(n)` — n = number of operations; each is processed in O(1).
- **Space:** `O(n)` — worst case every operation pushes a new score onto the stack.

**Decode String** (`3[ab2[c]]`) — push char by char; on `]`, pop back to `[`, peel **multi-digit** counts off with a positional multiplier, push the expanded string back. Twist is nesting + multi-digit numbers.
```cpp
if(ch == ']'){
    string temp_string = "";
    while(st.top() != "["){
        temp_string.insert(0, st.top());
        st.pop();
    }
    st.pop(); // pop the opening bracket

    int k = 0;
    int multiplier = 1;
    while(!st.empty() && isdigit(st.top()[0])){
        k += stoi(st.top()) * multiplier;   // rebuild multi-digit number
        st.pop();
        multiplier *= 10;
    }

    string replacement_string = "";
    for(int i = 0; i < k; i++){ replacement_string += temp_string; }
    st.push(replacement_string);
}
else{ st.push(string(1, ch)); }
```

- **Time:** `O(n · k)` — n = length of s, k = product of repeat counts; decoded output drives the work.
- **Space:** `O(n · k)` — nested `k[...]` repeats can blow up the decoded string size.

**Asteroid Collision** — a positive on the stack meets a negative arrival: simulate the fight by popping. Twist is the bookkeeping — a surviving negative and the leftover stack must land in the result **in order**, solved by writing into a pre-sized array at `fill_posi + st.size()`.
```cpp
if(ast < 0){ //this is a collision
    if(st.empty()){ result[fill_posi++] = ast; continue; }

    bool destroyed = false;
    while(!st.empty()){
        if(abs(ast) > st.top()){ st.pop(); }                        // arrival wins, keep fighting
        else if(abs(ast) < st.top()){ destroyed = true; break; }    // arrival dies
        else{ st.pop(); destroyed = true; break; }                  // both die
    }
    // IMPORTANT --> we need to ADD NEGATIVE ASTEROID TO RESULT IF IT SURVIVED ALL COLLISIONS
    if(!destroyed) result[fill_posi++] = ast;
}
else{ st.push(ast); }   // positive so no collision - hence just push

// drain leftover stack into the tail, in order
int stack_size_snapshot = st.size();
while(!st.empty()){
    result[fill_posi + st.size() - 1] = st.top();
    st.pop();
}
result.resize(fill_posi + stack_size_snapshot);
```

- **Time:** `O(n)` — n = number of asteroids; each is pushed and popped at most once.
- **Space:** `O(n)` — result array and stack each hold up to n asteroids.

---

## 3. Sort by arrival order, then collapse

**What it is:** you can't reason about who-affects-whom until things are lined up, so you sort first, then push each item and let it either start a new group or **merge** into the group on top. **Why it works:** after sorting by position, "does this one catch the one ahead?" becomes a single comparison against the stack top; whoever gets caught silently disappears into the fleet ahead. **Trigger:** "how many groups form," where membership depends on a rate/time relative to the item in front.

**Car Fleet** — sort by starting position descending, push *times-to-target*. A car whose time is `<=` the top caught up and merges (isn't pushed), so stack size = fleet count.
```cpp
sort(pairs.rbegin(), pairs.rend());   // by position, descending
stack<double> st;  //stores times

for(auto& pair: pairs){
    double distance = (target - pair.first);
    double time = distance / pair.second;

    if(st.empty() || time > st.top()){
        st.push(time);
    }
    // else it means that it got merged into a fleet 
}
return st.size();
```

- **Time:** `O(n log n)` — n = number of cars; dominated by sorting by start position.
- **Space:** `O(n)` — stack holds up to n fleet times.

---

## 4. Design: carry extra info per element

**What it is:** the O(1) query you want (min so far, FIFO order) isn't free from a bare stack, so each element carries side-info — or a second structure shadows the first. **Why it's clever:** MinStack encodes the *previous* minimum into the pushed value (`2*val - oldMin`) so pushing a new min is reversible on pop — O(1) `getMin()` with no extra array. **Trigger:** "design a stack/queue that also supports X in O(1)."

**Min Stack** — encode new minimums, decode on pop. Needs `long long` for overflow.
```cpp
void push(int val) {
    if (val >= minimum) { st.push(val); }
    else { // we got new minimum value
        long long oldMin = minimum;
        minimum = val;
        long long encoded = 2LL * val - oldMin;   // reversible encode
        st.push(encoded);
    }
}
void pop() {
    long long topVal = st.top();
    st.pop();
    if (topVal < minimum) { minimum = 2LL * minimum - topVal; }   // decode previous min
}
```

- **Time:** `O(1)` — every push/pop/getMin does constant work regardless of stack size.
- **Space:** `O(n)` — n = number of elements currently on the stack.

**Queue via Stacks / Stack via Queue** — force FIFO out of LIFO and vice-versa by reordering on every push.
```cpp
// MyQueue::push --> keep S1 permanently in FIFO order
while(!S1.empty()){ S2.push(S1.top()); S1.pop(); }
S1.push(x);
while(!S2.empty()){ S1.push(S2.top()); S2.pop(); }

// MyStack::push --> rotate so the newest sits at the front
q.push(x);
for(int i = 0; i < q.size() - 1; i++){ q.push(q.front()); q.pop(); }
```

- **Time:** `O(n)` push, `O(1)` pop — n = elements stored; each push eagerly re-sorts the structure.
- **Space:** `O(n)` — n = elements held across the two internal containers.

---

*Thread out of this topic: the **monotonic invariant** — keep the structure ordered so the thing you want is always at the boundary. It reappears as the never-decreasing `maxf` in Sliding Window — "window + frequency validity arithmetic", and as every heap in the Heaps topic.*
