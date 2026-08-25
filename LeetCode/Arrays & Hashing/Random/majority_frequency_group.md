# LC 3692 - Easy

# Python Code

## Approach 1:

might be bucket sort

brute -->
freq map
iterate through map and add in list
return one with max size

using an array instead of dict so that when i traverse afterwards --> the traversal naturally breaks the tie between sets with equal frequencies 

```python
class Solution:
    def majorityFrequencyGroup(self, s: str) -> str:
        
        freq = {}

        for char in s:
            freq[char] = freq.get(char, 0) + 1
        
        groups = [[] for _ in range (0, len(s) + 1)]

        for k, v in freq.items():
            groups[v].append(k)
        
        max_size = 0
        index = -1
        for i in range(0, len(groups)):
            if len(groups[i]) >= max_size:
                max_size = len(groups[i])
                index = i
        
        return ''.join(groups[index])
```
