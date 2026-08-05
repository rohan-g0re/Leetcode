# LC 468 - Medium

### INTUITION --> Use dots and colons as delimiters and then test the strings that remain 

```cpp
class Solution {

private:
    bool ipv4(string s){

        // 1. check delimiter count --> this is to make sure that our upcoming delimiter logic does not go wrong
        if(count(s.begin(), s.end(), '.') != 3) return false;


        // 2. delimiter valid --> get substring
        
        // 2.2 check if leading zeroes
        /*
        okay --> .0
        not okay --> .00 -- .01

        if starting zero then lenth should be 1 --> or else FUCKED up
        */
        
        int dots = 0;
        int i = 0;

        while(dots <= 3){

            int posi = s.find('.', i);
            string number = s.substr(i, posi - i);

            // check size
            if(number.size() <= 0 || number.size() > 3)  return false;
            
            // check leading zero case
            if(number[0] == '0' && number.size() > 1) return false;

            //check if is num  --> REMOVE IF ALPHABET OR SYMBOLS
            for(char c : number){
                if(!isdigit(c)) return false;
            }

            // check range
            if(stoi(number) > 255 || stoi(number) < 0) return false;

            // update i and dot count
            i = posi + 1;
            dots++;
        }
        return true;
    }



    bool ipv6(string s){

        // 1. check delimiter count --> this is to make sure that our upcoming delimiter logic does not go wrong
        if(count(s.begin(), s.end(),':') != 7) return false;

        int colons = 0;
        int i = 0;

        while(colons <= 7){

            int posi = s.find(':', i);
            string number = s.substr(i, posi - i);
            
            make sure the size is less than 4
            if(number.size() < 1 || number.size() > 4) return false; 


            // check alpha numerical --> if colon then false
            for(char c : number){

                /*
                reject when:
                    - not a number
                    - not in smallcase a-f
                    - not in capitalcase A-F
                */

                if(!isdigit(c) && !(tolower(c) >= 'a' && tolower(c) <= 'f')) return false;
            }

            // update i and dot count
            i = posi + 1;
            colons++;
        }
        return true;
    }

public:
    string validIPAddress(string queryIP) {

        if(ipv4(queryIP)) return "IPv4";
        if(ipv6(queryIP)) return "IPv6";

        return "Neither";
        
    }
};
```