
# Leetcode 2553 - Easy


### Intuition:
1. get each and every digit
2. Instead of interger to string conversion - we can also use %10 apporach but then we get the digits in reverse and that needs an additional temp array, which we need to reverse --> so i did not want to use additional array

```cpp
class Solution {
public:
    vector<int> separateDigits(vector<int>& nums) {

        vector<int> result;

        for (int num : nums){
            string number = to_string(num);
            for (char c : number){
                result.insert(result.end(), c - '0');
            }
        }
        return result;
    }
};
```


#### Same thing but using stack instead of the additional array

```cpp
class Solution {
public:
    vector<int> separateDigits(vector<int>& nums) {

        vector<int> result;
        stack<int> st;

        for(int i = nums.size() - 1; i >= 0; i--){

            int number = nums[i];

            while(number > 0){
                st.push(number % 10);
                number = number / 10;
            }
        }

        while(!st.empty()){
            result.push_back(st.top());
            st.pop();
        }

        return result;
    }
};


```



# BETTER --> In place reverse for result array

- just mark the size of result array before adding to it
- after the complete number is processed --> all digits that came after will be reversed

```cpp
class Solution {
public:
    vector<int> separateDigits(vector<int>& nums) {

        vector<int> result;
        int start = 0;

        for(int i = 0; i < nums.size(); i++){

            int number = nums[i];
            start = result.size();
            
            while(number > 0){
                result.push_back(number % 10);
                number = number / 10;
            }

            // new digits pushed should be reversed

            reverse(result.begin() + start, result.end())
        }

        return result;
    }
};


```