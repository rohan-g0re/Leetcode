## INTUITION

1. **follow / unfollow** --> simple hashmap of `follower --> set of followees`

2. **postTweet** --> just append `{time, tweetId}` for that user
   - global `time` counter keeps increasing --> so each user's tweet list is **sorted by time** (oldest at front, newest at back)

3. **getNewsFeed** --> **SAME AS MERGE K SORTED LISTS**

   - self + all followees = **k different sorted lists**
   - each list is sorted by time
   - we want the **most recent** tweets first --> start from the **back** of each list and use a **max-heap** on time
   - stop after 10 pops

##### Therefore heap will contain --> `< time , userId , index in that user's tweet list >`

- `time` bcoz it will be responsible for heapify() (default max-heap --> most recent on top)
- `userId` + `index` to jump to the **next older** tweet after we pop

```cpp
/*

DATA STRUCTURES:

1. tweets map  -->  userId : vector of {time, tweetId}
2. following map  -->  followerId : set of followeeIds
3. global time counter

getNewsFeed FLOW:

1. seed max-heap with the most recent tweet from self + every followee
2. pop top (most recent globally) --> append tweetId to answer
3. push the next older tweet from that same user (index - 1) if it exists
4. repeat until heap empty OR we have 10 tweets

*/


class Twitter {
private:

    int time; // needs to be set in the constructor so that we can start the time globally

    // followerId --> set of followeeIds
    unordered_map <int, unordered_set<int>> following;

    // userId --> list of {time, tweetId}  --> sorted by time bcoz we always push_back with increasing time
    unordered_map <int, vector<pair<int, int>>> tweets;


public:
    Twitter() {
        time = 0;
    }

    void postTweet(int userId, int tweetId) {

        tweets[userId].push_back({time, tweetId});

        // only updating time after a post is done --> because all other actions are done IRRESPECTIVE OF CURRENT TIME
        time++;
    }

    vector<int> getNewsFeed(int userId) {

        // heap <time, pair<userId, index>>
        priority_queue <pair<int, pair<int, int>>> max_heap;


        // helper --> seed heap with ONLY THE MOST RECENT TWEET of a user (if they have any)
        auto seed_heap = [&](int userid){

            if (tweets[userid].empty()) return;

            int idx = tweets[userid].size() - 1;   // back = most recent

            int curr_time = tweets[userid][idx].first;

            max_heap.push({curr_time, {userid, idx}});
        };


        // STEP 1: seed with self
        seed_heap(userId);


        // STEP 2: seed with every followee
        for (int followee : following[userId]){
            seed_heap(followee);
        }


        vector<int> result;


        // STEP 3: pop at most 10 --> same loop as merge k sorted lists
        while (!max_heap.empty() && result.size() < 10){

            int curr_time = max_heap.top().first;
            int uid = max_heap.top().second.first;
            int idx = max_heap.top().second.second;

            max_heap.pop();


            // append tweetId to answer
            result.push_back(tweets[uid][idx].second);


            /*
            IMPORTANT-GAME-CHANGER --> based on the userID you know which list to advance 
                --> HENCE, push next older tweet from same user if exists --> index - 1
            */

            if (idx > 0){
                idx--;
                max_heap.push({tweets[uid][idx].first, {uid, idx}});
            }
        }

        return result;
    }

    void follow(int followerId, int followeeId) {

        if (followerId == followeeId) return;

        following[followerId].insert(followeeId);
    }

    void unfollow(int followerId, int followeeId) {

        following[followerId].erase(followeeId);
    }
};
```
