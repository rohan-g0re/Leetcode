Given an input string s, reverse the order of the words.

A word is defined as a sequence of non-space characters. The words in s will be separated by at least one space.

Return a string of the words in reverse order concatenated by a single space.

Note that s may contain leading or trailing spaces or multiple spaces between two words. The returned string should only have a single space separating the words. Do not include any extra spaces.

Example 1:

Input: s = "the sky is blue"
Output: "blue is sky the"

Example 2:

Input: s = "  hello world  "
Output: "world hello"
Explanation: Your reversed string should not contain leading or trailing spaces.

Example 3:

Input: s = "a good   example"
Output: "example good a"
Explanation: You need to reduce multiple spaces between two words to a single space in the reversed string.

****************

## Intuition

- We need to reverse the order of words, not characters
- Multiple spaces should be reduced to single space
- Leading and trailing spaces should be removed
- We can split the string by spaces, filter out empty strings, reverse, and join

## BRUTE FORCE --> Split, Filter, Reverse, Join

```
class Solution {
public:
    string reverseWords(string s) {
        
        vector<string> words;
        stringstream ss(s);
        string word;
        
        // Split by spaces and collect non-empty words
        while (ss >> word) {
            words.push_back(word);
        }
        
        // Reverse the vector
        reverse(words.begin(), words.end());
        
        // Join with single space
        string result = "";
        for (int i = 0; i < words.size(); i++) {
            if (i > 0) result += " ";
            result += words[i];
        }
        
        return result;
    }
};
```

## BETTER --> Two Pass Approach

- First pass: Extract words from right to left
- Second pass: Build result string

```
class Solution {
public:
    string reverseWords(string s) {
        
        int n = s.length();
        string result = "";
        int i = n - 1;
        
        while (i >= 0) {
            
            // Skip trailing spaces
            while (i >= 0 && s[i] == ' ') {
                i--;
            }
            
            if (i < 0) break;
            
            // Extract word from right to left
            int j = i;
            while (j >= 0 && s[j] != ' ') {
                j--;
            }
            
            // Add word to result
            string word = s.substr(j + 1, i - j);
            if (result != "") {
                result += " ";
            }
            result += word;
            
            i = j;
        }
        
        return result;
    }
};
```

## OPTIMAL --> Single Pass with String Building

```
class Solution {
public:
    string reverseWords(string s) {
        
        int n = s.length();
        string result = "";
        int i = 0;
        
        while (i < n) {
            
            // Skip leading spaces
            while (i < n && s[i] == ' ') {
                i++;
            }
            
            if (i >= n) break;
            
            // Extract word
            int j = i;
            while (j < n && s[j] != ' ') {
                j++;
            }
            
            string word = s.substr(i, j - i);
            
            // Prepend word to result (reverse order)
            if (result == "") {
                result = word;
            } else {
                result = word + " " + result;
            }
            
            i = j;
        }
        
        return result;
    }
};
```

## TC --> O(n) where n is length of string
## SC --> O(n) for result string

