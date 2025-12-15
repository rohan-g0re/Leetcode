In a town, there are n people labeled from 1 to n. There is a rumor that one of these people is secretly the town judge.

If the town judge exists, then:

1. The town judge trusts nobody.
2. Everybody (except for the town judge) trusts the town judge.
3. There is exactly one person that satisfies properties 1 and 2.

You are given an array trust where trust[i] = [ai, bi] representing that the person labeled ai trusts the person labeled bi.

Return the label of the town judge if the town judge exists and can be identified, or return -1 otherwise.

Example 1:

Input: n = 2, trust = [[1,2]]
Output: 2

Example 2:

Input: n = 3, trust = [[1,3],[2,3]]
Output: 3

Example 3:

Input: n = 3, trust = [[1,3],[2,3],[3,1]]
Output: -1
Explanation: The person labeled 3 does not trust anyone, but person 1 trusts person 3, and person 3 trusts person 1, so person 3 cannot be the judge.

****************

## Intuition

- Town judge trusts nobody (outdegree = 0)
- Everyone trusts town judge (indegree = n - 1)
- We can track trust balance: decrease when someone trusts, increase when someone is trusted
- Town judge will have trust balance = n - 1

## BRUTE FORCE --> Count Indegree and Outdegree

- Count how many people each person trusts (outdegree)
- Count how many people trust each person (indegree)
- Find person with outdegree = 0 and indegree = n - 1

```
class Solution {
public:
    int findJudge(int n, vector<vector<int>>& trust) {
        
        vector<int> outdegree(n + 1, 0);
        vector<int> indegree(n + 1, 0);
        
        for (auto& t : trust) {
            outdegree[t[0]]++;  // Person t[0] trusts someone
            indegree[t[1]]++;    // Person t[1] is trusted
        }
        
        for (int i = 1; i <= n; i++) {
            if (outdegree[i] == 0 && indegree[i] == n - 1) {
                return i;
            }
        }
        
        return -1;
    }
};
```

TC --> O(n + trust.length)
SC --> O(n) for two arrays

## OPTIMAL --> Single Array (Trust Balance)

- Use single array to track trust balance
- Decrease balance when person trusts someone
- Increase balance when person is trusted
- Town judge has balance = n - 1

```
class Solution {
public:
    int findJudge(int n, vector<vector<int>>& trust) {
        
        vector<int> trustBalance(n + 1, 0);
        
        for (auto& t : trust) {
            trustBalance[t[0]]--;  // Person trusts someone, decrease balance
            trustBalance[t[1]]++;   // Person is trusted, increase balance
        }
        
        for (int i = 1; i <= n; i++) {
            if (trustBalance[i] == n - 1) {
                return i;
            }
        }
        
        return -1;
    }
};
```

## TC --> O(n + trust.length) where n is number of people
## SC --> O(n) for trust balance array

