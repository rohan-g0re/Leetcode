# LC 981 - Medium

# Intuition:
1. I can store the {timestamp, string} pairs in 2 ways:
    1. vector of pairs
    2. Linked List 

2. I can find the last valid entry in 2 ways:
    1. reverse linear search
    2. binary search

- hence I need to choose vector so that I can easily perform both search methods --> since with LL i will not have random access to perform binary search

## Code 1: Reverse Linear Search

```cpp

class TimeMap {

private:
    unordered_map<string, vector<pair<int, string>>> mp;
public:
    TimeMap() {}
    
    void set(string key, string value, int timestamp) {

        mp[key].push_back({timestamp, value});

        return;
        
    }
    
    string get(string key, int timestamp) {

        if(mp.find(key) != mp.end()){
            auto& store = mp[key];

            for(int i = store.size() - 1; i >= 0; i--){
                if(store[i].first <= timestamp){
                    return store[i].second;
                }
            }
        }

        return "";
        
    }
};


```


## Code 2: Binary Search

### Perform binary search on the index of the vector of pairs.

```cpp

class TimeMap {

private:
    unordered_map<string, vector<pair<int, string>>> mp;

    string binary_search(vector<pair<int, string>>& store, int timestamp){
        // i will be performing binary search on INDEXES and not on timestamp

        int low = 0;
        int high = store.size() - 1;

        int result = -1; // initially set to "NO VALID TIMESTAMP"

        while(low <= high){
            int mid = low + (high - low) / 2;

            if(store[mid].first <= timestamp){
                result = mid;
                low = mid + 1;
            }
            else{
                high = mid - 1;
            }
        }
        if(result == -1) return "";
        return store[result].second;
    }

public:
    TimeMap() {}
    
    void set(string key, string value, int timestamp) {

        mp[key].push_back({timestamp, value});

        return;
        
    }
    
    string get(string key, int timestamp) {

        if(mp.find(key) != mp.end()){
            auto& store = mp[key];

            return binary_search(store, timestamp);

        }

        return "";
        
    }
};

```