Given the head of a singly linked list, return true if it is a palindrome or false otherwise.

Example 1:

Input: head = [1,2,2,1]
Output: true

Example 2:

Input: head = [1,2]
Output: false

****************

## Intuition

- A palindrome reads the same forwards and backwards
- For linked list, we need to compare first half with reversed second half
- Steps:
  1. Find middle of list
  2. Reverse second half
  3. Compare first half with reversed second half

## BRUTE FORCE --> Convert to Array

- Convert linked list to array
- Check if array is palindrome

```
class Solution {
public:
    bool isPalindrome(ListNode* head) {
        
        vector<int> values;
        ListNode* curr = head;
        
        while (curr) {
            values.push_back(curr->val);
            curr = curr->next;
        }
        
        int left = 0;
        int right = values.size() - 1;
        
        while (left < right) {
            if (values[left] != values[right]) {
                return false;
            }
            left++;
            right--;
        }
        
        return true;
    }
};
```

TC --> O(n)
SC --> O(n)

## OPTIMAL --> Find Middle, Reverse Second Half, Compare

```
class Solution {
public:
    bool isPalindrome(ListNode* head) {
        
        if (!head || !head->next) return true;
        
        // Step 1: Find middle using slow and fast pointers
        ListNode* slow = head;
        ListNode* fast = head;
        
        while (fast->next && fast->next->next) {
            slow = slow->next;
            fast = fast->next->next;
        }
        
        // Step 2: Reverse second half
        ListNode* second = slow->next;
        slow->next = nullptr;  // Break the list
        
        ListNode* prev = nullptr;
        ListNode* curr = second;
        
        while (curr) {
            ListNode* next = curr->next;
            curr->next = prev;
            prev = curr;
            curr = next;
        }
        
        // Step 3: Compare first half with reversed second half
        ListNode* first = head;
        second = prev;  // prev is now head of reversed second half
        
        while (second) {
            if (first->val != second->val) {
                return false;
            }
            first = first->next;
            second = second->next;
        }
        
        return true;
    }
};
```

## TC --> O(n) where n is number of nodes
## SC --> O(1) constant space

