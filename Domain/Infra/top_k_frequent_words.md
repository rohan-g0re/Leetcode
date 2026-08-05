# LC 692 - Medium

## MAIN PATTERN --> Size-K heap + **CUSTOM COMPARATOR**

- freq map first
- then min-heap of size k
- BUT this time heap order is NOT just by freq --> also by **lexicographical order** when freqs match

---

## HOW IS THE CUSTOM COMPARATOR STRUCTURED?

```cpp
struct Custom_Comparator{
    bool operator()(pair<string, int>& a, pair<string, int>& b){
        // ...
    }
};
```

1. it is a **struct** that overloads `operator()`
2. `priority_queue` calls this like a function: `comp(a, b)`
3. it MUST return a `bool`
4. syntax when using it:

```cpp
priority_queue< pair<string, int>,
                vector<pair<string, int>>,
                Custom_Comparator
              > min_heap;
```

- template args = `<value_type, container, comparator>`
- without custom comparator --> default is `less<>` --> which makes a **max-heap**
- we pass our own --> so WE decide the order

---

## WHAT IS `bool operator()` ?

- it is the function the heap asks on every compare
- signature looks like a function call: `comp(a, b)`
- return type is `bool` --> and that bool IS the answer to one question only

#### HOW `true` / `false` CONVERTS TO AN ANSWER

- `true`  --> **YES**, `a` ranks below `b`
- `false` --> **NO**, `a` does NOT rank below `b`

That is it. The heap uses this yes/no to order the two nodes.

For our **min-heap** reading:
- the element that "ranks below" more often ends up closer to the **top**
- top = worst among the current k survivors = the one we `pop()` when size > k
- so when we return `true`, we are saying: `a` is **worse** than `b` for staying in the heap

---

## **Does A rank below B?**

> COMPLETE QUESTION IS --> Does `a` rank below `b` ?? --> `a` and `b` being the arguments, basically the 2 nodes being compared

This is the bold mental model for the whole comparator.

#### ALL SIGNS BELOW ARE W.R.T. A **MIN-HEAP**

We want:
- **lower freq** closer to top (easier to pop / evict when size > k)
- if freq same --> **lexicographically larger** word closer to top  
  (because the problem wants lexicographically **smaller** words preferred in the final top-k --> so the larger word is the one we should be ready to throw away)

```cpp
// 1. if freq dont match then answer to question comes from freq comparison
if(a.second != b.second) return a.second > b.second;

// 2. else --> freq match --> answer comes from string comparison
return a.first < b.first;
```

### WHY THIS EXACT SAME THING?

**Branch 1 — freqs differ:**
- `return a.second > b.second`
- if `a` has **higher** freq than `b` --> return `true` --> `a` ranks **below** `b`
- meaning: lower freq sits closer to the top of the min-heap
- this is the classic **min-heap by frequency** move

**Branch 2 — freqs match:**
- `return a.first < b.first`
- if `a` is lexicographically **smaller** than `b` --> return `true` --> `a` ranks **below** `b`
- meaning: the **larger** alphabetical word sits closer to the top (gets popped first if we must shrink)
- so among same frequency, we keep the lexicographically smaller ones inside the size-k heap

#### WHY W.R.T. MIN-HEAP SPECIFICALLY?
- size-k pattern: we keep only k survivors
- top of min-heap = **worst among survivors** = the one we pop when size > k
- so comparator must define "worse":
  - worse freq = smaller count
  - worse name (when tied) = lexicographically larger
- the `>` and `<` signs are written to encode exactly that "worse" definition for a **min-heap**, not a max-heap

---

# Code:

```cpp

class Solution {

private:

struct Custom_Comparator{
    bool operator()(pair<string, int>& a, pair<string, int>& b){

        // COMPLETE QUESTION IS --> Does a rank below b ?? --> a and b being the arguemnts, basically the 2 nodes being compared

        // 1. if freq dont match then answer to question come form freq comparison
        if(a.second != b.second) return a.second > b.second;
        
        // 2. else --> freq match --> answer conmes from string comparison
        return a.first < b.first;
    }
};

public:
    vector<string> topKFrequent(vector<string>& words, int k) {

        unordered_map<string, int> mp;

        // 1. fill the frequency map
        for(string word : words){
            mp[word]++;
        }

        // 2. push all in custom min_heap

        priority_queue< pair<string, int>,
        vector<pair<string, int>>,
        Custom_Comparator
        > min_heap;

        for(auto& pair : mp){
            min_heap.push({pair.first, pair.second});

            if(min_heap.size() > k) min_heap.pop();
        }


        // 3. fill vector in reverse fashion 

        vector<string> result(k);
        for(int i = k - 1; i>=0; i--){
            result[i] = min_heap.top().first;
            min_heap.pop();
        }
        return result;
    }
};

```
