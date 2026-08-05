# LC 359 - Medium

## Intuition --> maintain a map --> if new timing is previous timing + 10 --> true





```cpp


class Logger {

private:
    unordered_map<string, int> freq;

public:
    Logger() {}
    
    bool shouldPrintMessage(int timestamp, string message) {
        
        // if already there && after 10 seconds --> then update
        if(freq.find(message) != freq.end() && timestamp >= freq[message] + 10){
            // 1. update in map
            freq[message] = timestamp; 
            // 2. return true
            return true;
        }
        else{  // if not already there -- then insert
            freq[message] = timestamp;
            return true;
        }
        
        // if none of them - it means the word was there & 10 seconds were yet to happen --> so return false
        return false;
    }
};

```