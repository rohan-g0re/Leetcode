## Contains duplicate

## Valid Anagrams

- anagram is basically a word or phrase formed by
  --> RE-ARRANGING letters of a different word
  --> each original letter is used ONLY ONCE
- you can use a map - but the size is undefined
- so you can choose a frequency_map of 26 spaces built using a vector
- for that you need to convert every alpha to ascii number which is done using ``x - 'a'``

## Group Anagrams

- use a map :
  key --> sorted word
  value --> vector of original words that are made from alphabets in the key

## HEAP Syntax - MIN_HEAP

```cpp
priority_queue <pair<int, int>,
vector<pair<int, int>,
greater <pair<int, int>>
> min_heap;
```

## HEAP Syntax - MAX_HEAP

```cpp

// The default is max heap so dont need to declare extras stuff

priority_queue <pair<int, int>> max_heap;

```

**JUST LIKE MAP, WE CANT INITIALIZE HEAP WITH A PRE_DEFINED SIZE --> and so there will always be some other way of capping the size we are working on**

# 2 pointer

## Buy and Sell stocks - I

- **IT IS NOT NECESSARY that everytime the 2 pointer approach should start from either ends**
- Here it starts like a simple **i-j** which means i is lagging pointer to j








## PATTERNS to study : 
1. how do we generate all possible subarrays 



###### to do

1. Container with most water
2. **Longest substring wo repeating characters**
3. 
4. 
5. 
6. 
7. 
8. 
9. 
10. count number of inversions