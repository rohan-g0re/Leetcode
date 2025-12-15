You are given the head of a singly linked-list. The list can be represented as:

L0 → L1 → … → Ln - 1 → Ln

Reorder the list to be on the following form:

L0 → Ln → L1 → Ln - 1 → L2 → Ln - 2 → …

You may not modify the values in the list's nodes. Only nodes themselves may be changed.

Example 1:

Input: head = [1,2,3,4]
Output: [1,4,2,3]

Example 2:

Input: head = [1,2,3,4,5]
Output: [1,5,2,4,3]

****************

## Intuition

- We need to interleave nodes: first node, last node, second node, second-last node, etc.
- Steps:
  1. Find the middle of the list
  2. Reverse the second half
  3. Merge the two halves alternately

## BRUTE FORCE --> Store in Array and Rebuild

- Convert linked list to array
- Rebuild list using two pointers from start and end

```
class Solution {
public:
    void reorderList(ListNode* head) {
        
        vector<ListNode*> nodes;
        ListNode* curr = head;
        
        // Store all nodes in array
        while (curr) {
            nodes.push_back(curr);
            curr = curr->next;
        }
        
        int left = 0;
        int right = nodes.size() - 1;
        
        // Rebuild list
        while (left < right) {
            nodes[left]->next = nodes[right];
            left++;
            
            if (left >= right) break;
            
            nodes[right]->next = nodes[left];
            right--;
        }
        
        nodes[left]->next = nullptr;
    }
};
```

TC --> O(n)
SC --> O(n)

## OPTIMAL --> Three Steps: Find Middle, Reverse Second Half, Merge

```
class Solution {
public:
    void reorderList(ListNode* head) {
        
        if (!head || !head->next) return;
        
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
        
        // Step 3: Merge two halves
        ListNode* first = head;
        second = prev;  // prev is now head of reversed second half
        
        while (second) {
            ListNode* temp1 = first->next;
            ListNode* temp2 = second->next;
            
            first->next = second;
            second->next = temp1;
            
            first = temp1;
            second = temp2;
        }
    }
};
```

## TC --> O(n) where n is number of nodes
## SC --> O(1) constant space

