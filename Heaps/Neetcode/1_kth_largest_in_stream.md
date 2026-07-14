
### MY CODE 

```cpp

/*

kth highest test score

k - given, 
MAINTAINS stream of test scores
return k after new added 


*/

class KthLargest {
private: 

    priority_queue<int, vector<int>, greater <int>> heap;

    int kx;

    // EXTRA: declare stream
    // vector <int> stream;

public:
    KthLargest(int k, vector<int>& nums) {

        // initialize k and create the heap too because we will lose the access to these values once the constructor ends

        kx = k;

        // EXTRA: if ever we needed to keep the stream intact with us then we would keep that as well

        // stream = nums;


       
        for(int element : nums){
            heap.push(element);
            if (heap.size() > kx) heap.pop();
        }


        
    }
    
    int add(int val) {

        // EXTRA: add it to stream as well
        // stream.push_back(val);

        heap.push(val);

        if (heap.size() > kx) heap.pop();

        return heap.top();

        
    }
};


```

