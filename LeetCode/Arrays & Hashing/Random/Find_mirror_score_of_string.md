
# LeetCode 3412 - Medium


## BRUTE FORCE:

1. we start iterating on string - and get j
2. we start a nested loop from j -> 0 and check logic for every i
3. If valid, we mark it in the visited array 


## BETTER: keep a freq map of past letters 

### IMPORTANT NOTE -- we also need indexes to calculate the score therefore we need indexes as well --> hence use vector to store indexes (instead of freq)





```cpp
class Solution {
public:
    long long calculateScore(string s) {

        long long score = 0;

        // step 0 - initializing empty map
        unordered_map<char, vector<int>> mp;

        for(char ch = 'a'; ch <= 'z'; ch++){
            mp[ch] = vector<int>();
        }



        for(int i = 0; i < s.size(); i++){
            
            // 1. calculate mirror
            char mirror = 'z' - (s[i]- 'a');

            // 2. if mirror in map then
                // - remove tail - since it will be the CLOSEST mirror
                // - add to score
                // - pop it

            if (mp[mirror].size() > 0){
                
                int j = mp[mirror].back();

                score += i - j;
                
                mp[mirror].pop_back();
            }
            // 3. if no mirror then add current
            else{
                mp[s[i]].push_back(i);
            }
        }
        return score;
    }
};
```