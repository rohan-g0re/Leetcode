## INTUITION:

- if anyone pays 5 --> increment five --> continue

- if anyone pays 10
    - --> increment ten
    - --> decrement five if possibile
        - --> if fives not there: return false

- if anyone pays 20
    - --> increment twenty
    - --> DECREMENT:
        - --> if payout >= 10 --> decrement tens
        - --> else decrement fives


```cpp

class Solution {
public:
    bool lemonadeChange(vector<int>& bills) {

        int fives = 0;
        int tens = 0;
        int twenties = 0;


        for(int bill : bills){

            if (bill == 5){
                fives++;
                continue;
            }

            else if (bill == 10){
                tens++;

                // 1. return 5 
                if (fives > 0){
                    fives--;
                    continue;
                }
                // 2. return false
                else return false;
            }

            // bill == 20
            else{
                twenties++;

                int payout = 15;

                while(payout > 0){
                    if (payout >= 10 && tens > 0){
                        tens--;
                        payout -= 10;
                    }
                    else if (fives > 0){
                        fives--;
                        payout -= 5;
                    }
                    else return false;
                }
            }
        }
        return true;
    }
};

```