## Process the logs and calculate the avg latency

```cpp

#include <bits/stdc++.h>
using namespace std;


class Solution{

public:
    double avg(string str){
        
        vector<vector<string>> logs(6, vector<string>());
        
        int i = 0;
        int counter = 0;
        int n = str.size();
        
        
        // STEP 1: grid fill
        while(i < n){
            
            int posi = str.find(i, '\n');
            string line = str.substr(i, posi - i);
            
            
            // process this string
            int j = 0;
            int m = line.size();
            
            while(counter > 0 && j < m){
                
                if(line.find(' ') != string::npos){
                    
                    int posi = line.find(' ');
                    string ele = line.substr(j, posi - j);
                    
                    logs[counter - 1].push_back(ele);
                    
                    // incr j
                    j = posi + 1;
                    continue;
                    
                }
                break;
            }
            
            // incr i & counter
            
            i = posi + 1;
            counter++;            
        }
        
        
        
        
        for(auto& line : logs){
            for(string ele : line){
                cout<<ele;
            }
        }
               
        
        // STEP 2 - calculating average --> DID NOT COMPLETE
        
        return 0.0;
    }
};


int main(){
    
    
    string log_data = R"([Timestamp] [Client_IP] [Method] [Path] [Status_Code] [Latency]
2026-02-25T09:15:05Z 192.168.1.45 GET /index.html 200 45ms
2026-02-25T09:15:12Z 10.0.0.12 POST /api/v1/upload 201 3402ms
2026-02-25T09:15:18Z 172.16.254.1 GET /login 302 12ms
2026-02-25T09:15:22Z 192.168.1.1 PUT /api/v1/user/settings 403 88ms
2026-02-25T09:15:30Z 192.168.1.104 GET /static/css/main.css 304 5ms
2026-02-25T09:15:45Z 10.0.0.5 DELETE /api/v1/video/99 204 450ms
2026-02-25T09:16:01Z 192.168.1.1 GET /admin 404 110ms
2026-02-25T09:16:15Z 172.16.0.22 POST /api/v1/auth/mfa 401 210ms)";

    
    Solution S;
    double average a= S.avg(log_data);
    cout<<average;
    
}


```