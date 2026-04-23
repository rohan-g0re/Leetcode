

## BRUTE

```cpp

class Solution {
public:
    int hIndex(vector<int>& citations) {

        int g_max = 0;

        int n = citations.size();

        for(int index = 0; index <= n; index++){
            
            int cnt = 0;

            for(int cites : citations){
                if (cites >= index){
                    cnt++;
                }
            }

            if (cnt >= index) g_max = max(g_max, index);

        }

        return g_max;
        
    }
};


```



## OPTIMAL

#### INTUITION --> we just need to compare if ith paper has atleast i citations --> as this is in descending order, only citations[i] needs to satisfy the conditino of being greater than i --> since we know that all other were greater than it already


#### IMPORTANT NOTE --> State space has 1-based indexing --> therefore our array accesses should have `i-1` to handle the case for `n` as it is a valid answer
```cpp

class Solution {
public:
    int hIndex(vector<int>& citations) {

        sort(citations.rbegin(), citations.rend());
        int n = citations.size();
        
        int cnt = 0;
        
        for(int i = 1; i <= n; i++){ // state space --> increments by 1 but will only go till size

            if (citations[i-1] >= i){
                cnt++;
            }
            else break;
        }
        return cnt;
    }
};

```