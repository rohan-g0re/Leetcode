## INTUITION:
1. We have to recursively split the domain wrt DOT 
2. Also while splitting we need to remember what VISIT_COUNT it comes with
3. IMPORTANT --> I think we are supposed to use hashmap where key is domain and value is visits
- I also dont know how to split the string wrt space (for count) and wrt DOT(for domain and subdomains)

## ATTEMPT 1: 

1. Write a loop over the input array 
    - pick a string 
    - split wrt space --> we get count and lowest domain 
    - write another loop to go over the domain 
        - split wrt DOT (no dot(complete), first dot, second dot,.....) 
        - Choose that domain and look up in MAP 
            - if already there --> ++ visit count
            - if not --> add the key and value 

**INTUITION  --> during splitting we need to convert the count into integer**

#### INTUTION --> the splitting gets UNNECESSARY COMPLEX using the find function --> instead lets traverse char by char and use substr to get domains and sub-doamins


```cpp
class Solution {
public:
    vector<string> subdomainVisits(vector<string>& cpdomains) {

        unordered_map <string, int> count_map;


        for (auto& given_string : cpdomains){


            // 1. split the string into "int" count && lowest_domain 

            int space_posi = given_string.find(" ");

            int visit_count = stoi ( given_string.substr(0, space_posi) );
          
            
            
            // 2. Loop over every subdomain over branch;

            
            for (int i = space_posi; i < given_string.size(); i++){

                // we purposefullly start from space so that we can have THE COMPELTE DOMAIN AS WELL 


                // the dot case is for all other subdomains
                // the space case is for getting the complete given_domain 

                if (given_string[i] == ' ' || given_string[i] == '.'){
                    string current_domain = given_string.substr(i+1);
                    count_map[current_domain] += visit_count;
                }
            }
 
        }

        // 3. adding the map to result vector 

        vector <string> result;

        for (auto& pair : count_map){
            string domain = pair.first;
            string count = to_string (pair.second);
            string temp = count + " " + domain ;

            result.push_back(temp);

        }

        return result;


        
    }
};
```


## Syntax Learnings 
1. string.substr(param_1: starting_position, param_2: how_much_length_after_start)
2. string.erase(param_1: starting_position, param_2: how_much_length_after_start)


#### Code snippet which was not used but can be useful 

```cpp

string space_delimiter = " ";
vector<string> words{};
int pos = 0;

while ((pos = text.find(space_delimiter)) != string::npos) {
    words.push_back(text.substr(0, pos));
    text.erase(0, pos + space_delimiter.length());
}
```