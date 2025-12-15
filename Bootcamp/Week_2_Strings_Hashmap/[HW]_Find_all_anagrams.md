Given two strings s and p, return an array of all the start indices of p's anagrams in s. You may return the answer in any order.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

Example 1:

Input: s = "cbaebabacd", p = "abc"
Output: [0,6]
Explanation:
The substring with start index = 0 is "cba", which is an anagram of "abc".
The substring with start index = 6 is "bac", which is an anagram of "abc".

Example 2:

Input: s = "abab", p = "ab"
Output: [0,1,2]
Explanation:
The substring with start index = 0 is "ab", which is an anagram of "ab".
The substring with start index = 1 is "ba", which is an anagram of "ab".
The substring with start index = 2 is "ab", which is an anagram of "ab".

****************

## Intuition

- We need to find all substrings in s that are anagrams of p
- An anagram means same characters with same frequency
- Use sliding window technique with frequency map
- Window size = length of p
- Compare frequency maps of window and p

## BRUTE FORCE --> Check every substring

For each starting position, check if substring is anagram of p

```
class Solution {
public:
    vector<int> findAnagrams(string s, string p) {
        
        vector<int> result;
        int n = s.length();
        int m = p.length();
        
        if (n < m) return result;
        
        // Sort p for comparison
        sort(p.begin(), p.end());
        
        for (int i = 0; i <= n - m; i++) {
            string substr = s.substr(i, m);
            sort(substr.begin(), substr.end());
            
            if (substr == p) {
                result.push_back(i);
            }
        }
        
        return result;
    }
};
```

TC --> O(n * m * log(m)) where n = len(s), m = len(p)

## BETTER --> Sliding Window with Frequency Map

- Use hashmap to count character frequencies
- Maintain a sliding window of size m
- Compare frequency maps

```
class Solution {
public:
    vector<int> findAnagrams(string s, string p) {
        
        vector<int> result;
        int n = s.length();
        int m = p.length();
        
        if (n < m) return result;
        
        // Frequency map for p
        vector<int> pFreq(26, 0);
        for (char c : p) {
            pFreq[c - 'a']++;
        }
        
        // Frequency map for current window
        vector<int> windowFreq(26, 0);
        
        // Initialize window
        for (int i = 0; i < m; i++) {
            windowFreq[s[i] - 'a']++;
        }
        
        // Check first window
        if (windowFreq == pFreq) {
            result.push_back(0);
        }
        
        // Slide the window
        for (int i = m; i < n; i++) {
            // Remove leftmost character
            windowFreq[s[i - m] - 'a']--;
            
            // Add new character
            windowFreq[s[i] - 'a']++;
            
            // Check if window matches p
            if (windowFreq == pFreq) {
                result.push_back(i - m + 1);
            }
        }
        
        return result;
    }
};
```

## TC --> O(n) where n is length of s
## SC --> O(1) since we use fixed size arrays (26 characters)

