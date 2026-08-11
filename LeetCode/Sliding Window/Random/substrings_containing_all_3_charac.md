

# LC 1358 - Medium

## BRUTE: 

- generate all strings
- add to the count if counts match

```cpp

class Solution {
public:
    int numberOfSubstrings(string s) {

        int n = s.size();
        int counter = 0;

        for(int i = 0; i < n; i++){
            
            // map for just making sure that we have 3 values in it
            unordered_map<char, int> mp;

            for(int j = i; j < n; j++){

                // 1. mark present
                mp[s[j]]++;

                // 2. if all are present --> inc. counter 
                if(mp.size() == 3) counter++;

            }
        }
        return counter;
        
    }
};

```


## BRUTE 2 - Short Circuit the inner for loop

#### INTUITION --> if we reach such an 'index j' where the condition is true --> then all the next indexes are also going to return true --> hence when we reach that index: instead of doing counter++ --> we can directly add the remaining count of indexes into it


```cpp

class Solution {
public:
    int numberOfSubstrings(string s) {

        int n = s.size();
        int counter = 0;

        for(int i = 0; i < n; i++){
            
            // map for just making sure that we have 3 values in it
            unordered_map<char, int> mp;

            for(int j = i; j < n; j++){

                // 1. mark present
                mp[s[j]]++;

                // 2. if all are present --> inc. counter 
                if(mp.size() == 3){
                    
                    counter += (n - j); // this add the current as well as remaining
                    break;
                }
            }
        }
        return counter;
    }
};


```


# OPTIMAL - Going to call this **"Reverse Treadmill Walk"** --> because we are moving ahead but constantly looking back (we dont care about the future) 

# IDEA: "This letter is the last character of which tightest valid string"

### INTUITIONS: we use the same index trick from brute 2 to calculate the total amount of strings --> but there is a main requirement: Just like we calculated total addable strings after first success in brute2 --> HERE we are going to count strings WITH RESPECT TO MIN LENGTH required to make a successful string.

#### How do we do this???? --> maintain 3 indexes of "When did I last see it" --> if both are non-zero, THEIR MINIMUM is where your **TIGHTEST STRING STARTS** --> everything before that can be added directly


```cpp

class Solution {
public:
    int numberOfSubstrings(string s) {

        int n = s.size();
        int counter = 0;
        
        unordered_map<char, int> mp;
        mp.insert({a, -1});
        mp.insert({b, -1});
        mp.insert({c, -1});


        for(int i = 0; i < n; i++){
            
            // 1. mark this index for the correct letter
            mp[s[i]] = i

            // 2. check if all are present
            if(mp[a] != -1 && mp[b] != -1 && mp[c] != -1){
                // find minimum 

                int start = min(mp[a], min(mp[b], mp[c]));

                counter += start+1;
            }
        }
        return counter;
    }
};

```


