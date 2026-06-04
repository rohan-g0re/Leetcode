## BRUTE:

- need to check every number until it is atleast 3 digit
- After that --> check from the second digit if its a valley or peak 
- if yes then go to next digit 

### **IMPORTANT NOTE -->  we are directly comparuing the characters as numbers in form of char still follow lexico order --> we can also convert the respective chars into integer by subtracting zero like --> `char left = number[digit - 1] - '0'`**

```cpp

class Solution {
public:
    int totalWaviness(int num1, int num2) {

        int waviness = 0;



        for(int i = num1; i <= num2; i++){

            // 1. check if number has atleast 3 digits

            string number = to_string(i);
            int n = number.size();

            if(n > 2){

                // 2. start peak-valley check loop on every digit

                for(int digit = 1; digit < n - 1; digit++){


                    char left = number[digit - 1];      
                    char main = number[digit];
                    char right = number[digit + 1]; 

                    // 2.1 check if given digit is peak OROROROR 2.2 it is a valley

                    if ((left < main && right < main) || (left > main && right > main)) waviness++;

                }
            }
        }

        return waviness;
    }
};

```