

## Contains duplicate 

## Valid Anagrams
- anagram is basically a word or phrase formed by
    --> RE-ARRANGING letters of a different word
    --> each original letter is used ONLY ONCE

- you can use a map - but the size is undefined 
- so you can choose a frequency_map of 26 spaces built using a vector 
- for that you need to convert every alpha to ascii number which is done using ```x - 'a'``` 


## Group Anagrams
- use a map :
    key --> sorted word
    value --> vector of original words that are made from alphabets in the key

## HEAP Syntax 

priority_queue <pair<int, int>,
vector<pair<int, int>,
greater <pair<int, int>>
> min_heap;

**JUST LIKE MAP, WE CANT INITIALIZE HEAP WITH A PRE_DEFINED SIZE --> and so there will always be some other way of capping the size we are working on**


# 2 pointer

## Buy and Sell stocks - I 
- **IT IS NOT NECESSARY that everytime the 2 pointer approach should start from either ends**

- Here it starts like a simple **i-j** which means i is lagging pointer to j




####### to do 
1. Container with most water 
2. Longest substring wo repeating characters
3. 
4. move zeroes 
5. second largest element in array without sorting
6. Next permutation
7. max subarrray sum
8. Majority element n/3
9. max prod sub array 
10. number of inversions