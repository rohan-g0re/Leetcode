

# INTUITION:

1. We basically need to maintain a pivot such that all the elements before it are A's and the elements after it are B's.

2. We count removals my sum of B's in the left side of the pivot and A's in the right side.


### IMPORTANT INSIGHT --> it does NOT matter if the PIVOT ELEMENT is A or B because --> because it will either be the last A or the first B --> So whatever the pivot element is (A or B), it will not be counted in both of the counts (B's at left && A's at right). 

```cpp
class Solution {
public:
    int minimumDeletions(string s) {



        // making an array to store count of A's to the right of a given index (kinda like suffix sum)
        int n = s.size();
        vector<int> count_right_a (n, 0);

        // STEP 1: fill A counts array

        // count_right_a[n-1] = 0 --> since NO right elements

        for (int i = n-2; i >=0; i--){

            // if last was a --> increment value
            if (s[i+1] == 'a') count_right_a[i] = count_right_a[i + 1] + 1;

            // else stay the same as before --> which means moving did not reveal an A --> it revealed a B
            else count_right_a[i] = count_right_a[i + 1];
        }


        // STEP 2: Look at B count && calculate min_removals (by adding wrong As and Bs) && THEN INCREMENT THE COUNT OF B BEFORE MOVING TO THE RIGHT

        
        int min_removals = n;

        int count_left_b = 0; // zero at the beginning because no elements to the left.
        

        for (int i = 0; i < n; i++){

            // 2.1 calculate min_removals

            min_removals = min (min_removals, count_left_b + count_right_a[i]);

            // 2.2 update B count for next iteration

            if (s[i] == 'b') count_left_b++;
        }

        return min_removals;
        
    }
};

```


# OPTIMAL --> Dont Use Extra Space for the count A array.

## 1. Instead we count the total number of A's in an individual iteration and then while moving we update the count of A similar to how we update the count of B.

## 2. Only thing is that we need to update A BEFORE calculating the removals whereas B is updated AFTER calculating the removals.

```cpp

/*

INTUITION:

1. We basically need to maintain a pivot such that all the elements before it are A's and the elements after it are B's.

2. We count removals my sum of B's in the left side of the pivot and A's in the right side.


IMPORTANT INSIGHT --> it does NOT matter if the PIVOT ELEMENT is A or B because --> because it will either be the last A or the first B --> So whatever the pivot element is (A or B), it will not be counted in both of the counts (B's at left && A's at right). 


*/



class Solution {
public:
    int minimumDeletions(string s) {

        // making an array to store count of A's to the right of a given index (kinda like suffix sum)
        int n = s.size();
        int count_right_a = 0;

        // STEP 1: count total A's

        for (char c : s){
            if (c == 'a') count_right_a++;
        }


        // STEP 2: Update A count && calculate min_removals (by adding wrong As and Bs) && Update B count

        
        int min_removals = n;

        int count_left_b = 0; // zero at the beginning because no elements to the left.
        

        for (int i = 0; i < n; i++){

            // 2.1 update A count

            if (s[i] == 'a') count_right_a--;

            // 2.2 calculate min_removals

            min_removals = min (min_removals, count_left_b + count_right_a);

            // 2.3 update B count for next iteration

            if (s[i] == 'b') count_left_b++;
        }

        return min_removals;
        
    }
};

```