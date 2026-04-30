

## FAILED approach --> I used double queue but this approach only passes 73/84 cases bcoz our parties are not using the "SMART" strategy --> **SINCE when R comes we might be deleting a D which has ALREADY VOTED (there is no way of finding if the D being banned is the one who is YET TO VOTE) And we want to ban a D which is yet to vote.**

```cpp
/*

INTUITION:
- i think we need to keep a count of R and D's
- for every round --> for every check --> we need to check if any of the party has reached zero


# COOKING SOMETHING

1. can we have 2 queues --> one for r and d
---> we push indices in queues

2. if we reach zero then happy
3. for banning we just replace str with #



*/





class Solution {
public:
    string predictPartyVictory(string senate) {

        int n = senate.size();
        // 1. fill both queues

        queue<int> r_indices;
        queue<int> d_indices;

        for(int i = 0; i < n; i++){
            if(senate[i] == 'D') d_indices.push(i);
            else r_indices.push(i);
        }

        // 2. forward pass

        while(r_indices.size() != 0 && d_indices.size() != 0){

            // simulate a pass

            for(int i = 0; i < n; i++){

                // - base case --> # --> ignore
                if(senate[i] == '#') continue;


                // if R 

                else if(senate[i] == 'R'){

                    // - if d over then return 
                    if(d_indices.size() == 0) return "Radiant";

                    // if d remaining then ban
                    else{
                        // replace --> (startposi, length, target_string)
                        senate.replace(d_indices.front(), 1, "#");
                        d_indices.pop();
                    }

                }

                // if D

                else{ // if(senate[i] == 'D'){

                    // - if r over then return 
                    if(r_indices.size() == 0) return "Dire";

                    // if r remaining then ban
                    else{
                        // replace --> (startposi, length, target_string)
                        senate.replace(r_indices.front(), 1, "#");
                        r_indices.pop();
                    }

                }
            }
        }


        if(r_indices.size() == 0) return "Dire";

        return "Radiant";
        
    }
};





```



# CORRECT APPROACH --> SIMULATING FIGHT BETWEEN INDICES --> the winner gets pushed in queue again, the loser is popped --> also mainitaing the magnitude of index as we need to make sure that for the simulation of multiple rounds, the index repushed is not the original one as it might "LOSE" to an index from a previous round


```cpp


class Solution {
public:
    string predictPartyVictory(string senate) {

        int n = senate.size();
        // 1. fill both queues

        queue<int> r_indices;
        queue<int> d_indices;

        for(int i = 0; i < n; i++){
            if(senate[i] == 'D') d_indices.push(i);
            else r_indices.push(i);
        }

        // 2. forward pass

        while(r_indices.size() != 0 && d_indices.size() != 0){

            // pop earliest two contenders

            int r = r_indices.front();
            int d = d_indices.front();
            r_indices.pop();
            d_indices.pop();

            // the lower one wins and gets inserted again in the queue

            if(r < d){ // r wins --> repush r with  new index

                r_indices.push(r+n); // r+n to preserve original index spacing --> or else we can also use n++ which makes sure increasing order of indices --> both would work as we only need the relationship between their magnitude

            }
            else{
                d_indices.push(d+n);
            }
        }

        return (r_indices.size() == 0) ? "Dire" : "Radiant";
    
    }
};


```