Implement the myAtoi(string s) function, which converts a string to a 32-bit signed integer (similar to C/C++'s atoi function).

The algorithm for myAtoi(string s) is as follows:

1. Read in and ignore any leading whitespace.
2. Check if the next character (if not already at the end of the string) is '-' or '+'. Read this character in if it is either. This determines if the final result is negative or positive respectively. Assume the result is positive if neither is present.
3. Read in next the characters until the next non-digit character or the end of the string is reached. The rest of the string is ignored.
4. Convert these digits into an integer (i.e. "123" -> 123, "0032" -> 32). If no digits were read, then the integer is 0. Change the sign as necessary (from step 2).
5. If the integer is out of the 32-bit signed integer range [-231, 231 - 1], then clamp the integer so that it remains in the range. Specifically, integers less than -231 should be clamped to -231, and integers greater than 231 - 1 should be clamped to 231 - 1.
6. Return the integer as the final result.

Note:
- Only the space character ' ' is considered a whitespace character.
- Do not ignore any characters other than the leading whitespace or the rest of the string after the digits.

Example 1:

Input: s = "42"
Output: 42
Explanation: The underlined characters are what is read in, the caret is the current reader position.
Step 1: "42" (no characters read because there is no leading whitespace)
         ^
Step 2: "42" (no characters read because there is neither '-' nor '+')
         ^
Step 3: "42" ("42" is read in)
           ^
The parsed integer is 42.
Since 42 is in the range [-231, 231 - 1], the final result is 42.

Example 2:

Input: s = "   -42"
Output: -42
Explanation:
Step 1: "   -42" (leading whitespace is read and ignored)
            ^
Step 2: "   -42" ('-' is read, so the result is negative)
             ^
Step 3: "   -42" ("42" is read in)
               ^
The parsed integer is -42.
Since -42 is in the range [-231, 231 - 1], the final result is -42.

Example 3:

Input: s = "4193 with words"
Output: 4193
Explanation:
Step 1: "4193 with words" (no leading whitespace)
         ^
Step 2: "4193 with words" (no '-' or '+' sign)
         ^
Step 3: "4193 with words" ("4193" is read in; reading stops because the next character is a non-digit)
              ^
The parsed integer is 4193.
Since 4193 is in the range [-231, 231 - 1], the final result is 4193.

****************

## Intuition

- Parse string step by step following the algorithm
- Handle whitespace, sign, digits, and overflow
- Use long long to detect overflow before clamping

## BRUTE FORCE --> Follow Algorithm Step by Step

```
class Solution {
public:
    int myAtoi(string s) {
        
        int n = s.length();
        int i = 0;
        
        // Step 1: Skip leading whitespace
        while (i < n && s[i] == ' ') {
            i++;
        }
        
        if (i >= n) return 0;
        
        // Step 2: Check for sign
        int sign = 1;
        if (s[i] == '-') {
            sign = -1;
            i++;
        } else if (s[i] == '+') {
            i++;
        }
        
        // Step 3: Read digits
        long long result = 0;
        while (i < n && isdigit(s[i])) {
            result = result * 10 + (s[i] - '0');
            
            // Step 5: Check for overflow
            if (sign * result > INT_MAX) {
                return INT_MAX;
            }
            if (sign * result < INT_MIN) {
                return INT_MIN;
            }
            
            i++;
        }
        
        return sign * result;
    }
};
```

## OPTIMIZED --> Early Overflow Detection

```
class Solution {
public:
    int myAtoi(string s) {
        
        int n = s.length();
        int i = 0;
        
        // Skip whitespace
        while (i < n && s[i] == ' ') {
            i++;
        }
        
        if (i >= n) return 0;
        
        // Handle sign
        int sign = 1;
        if (s[i] == '-') {
            sign = -1;
            i++;
        } else if (s[i] == '+') {
            i++;
        }
        
        // Read digits with overflow check
        long long num = 0;
        while (i < n && isdigit(s[i])) {
            num = num * 10 + (s[i] - '0');
            
            // Check overflow before continuing
            if (sign * num > INT_MAX) {
                return INT_MAX;
            }
            if (sign * num < INT_MIN) {
                return INT_MIN;
            }
            
            i++;
        }
        
        return sign * num;
    }
};
```

## TC --> O(n) where n is length of string
## SC --> O(1) constant space

