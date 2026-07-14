## INTUITION
- was thinking of heap but cant do that SINCE we will not know numbers which come after it 
- GOOD INSIGHT --> k closest element are the one positionally closest to them --> so we need to start checking the left and right elements of the x --> therefore search for x and setup 2 pointers for it which move away from each other
    - but x can be not present in the array as well --> in this case we use "UPPER BOUND" concept from binary search and hence we can find the position which makes the most sense (<= x) 


##### SECOND THOUGHTS on heap  (maybe we can try later) --> can build a max heap of size k where the elements are <difference, key> --> when complete traversal is done: pop all from heal and put in array 


```cpp

class Solution {

private:
    int binary_search(vector<int>& arr, int x){
        int start = 0;
        int end = arr.size() - 1;


        int result = arr.size();

        while (start <= end){

            int mid = start + (end-start) / 2;
            
            if(arr[mid] >= x){
                result = mid;
                end = mid - 1;
            }
            else{
                start = mid + 1;
            }

        }

        return result;

    }

public:
    vector<int> findClosestElements(vector<int>& arr, int k, int x) {

        int n = arr.size();

        // 1. find element index using binary search - upper bound

        int index = binary_search(arr, x);

        /*
        2. initiate 2 pointer on that index 
            - push the arr[mid]
            - NEXT:
                - it can pick both left and right if we have k = 2 left
                - it needs to check boundaries of array while l-- and r++
                - k -= 2 everytime
                - when k reaches 1 pick by comparing l and r

        */


        vector <int> result;
        
        // this declaration can go out of bounds but it will be taken care of: by the while loop condition
        
        int r = 0;
        if (index < n) r = index;
        else r = n;
        
        int l = r - 1;                         // l = r-1, could be -1, guarded by loops

        while(k > 0 && l >= 0 && r < n){
            
            if ( abs (arr[l] - x) <= abs(arr[r] - x) ){  // picking the left when a tie happens
                result.push_back(arr[l]);
                l--;
            }
            else{
                result.push_back(arr[r]);
                r++;
            }

            k--;

        }

        while (k > 0 && l >= 0){
            result.push_back(arr[l]);
            l--;
            k--;
        }

        while (k > 0 && r < n){
            result.push_back(arr[r]);
            r++;
            k--;
        }

        sort(result.begin(), result.end());
        return result;

    }
};

```