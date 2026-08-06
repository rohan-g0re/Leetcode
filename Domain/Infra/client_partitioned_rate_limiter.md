# Client Partitioned Rate Limiter

- allow at most `maxRequests` hits per `user` inside a sliding window of `windowSize`
- each client/user is partitioned separately --> map of `user -> queue of timestamps`
- before deciding: evict timestamps that fell out of the window, then accept if queue still has room

# Question:

Design a rate limiter that throttles requests **independently for each user**.

The limiter is configured once with two values, `maxRequests` and `windowSize`, and these apply identically to every user. A request from a user at time `timestamp` is **allowed** if that user has made fewer than `maxRequests` allowed requests in the half-open time window `(timestamp - windowSize, timestamp]`. Otherwise the request is **denied**.

A denied request does not count against the user's quota — only allowed requests occupy a slot in the window.

Implement the `RateLimiter` class:

- `RateLimiter(int maxRequests, int windowSize)` initializes the limiter so that each user may make at most `maxRequests` requests in any `windowSize` seconds.
- `boolean isAllowed(String userId, int timestamp)` returns `true` if the request from `userId` at time `timestamp` (in **seconds**) is permitted, and `false` otherwise.

It is guaranteed that all calls to `isAllowed` are made with **non-decreasing** values of `timestamp`.

---

## Example 1

**Input**

```
["RateLimiter", "isAllowed", "isAllowed", "isAllowed", "isAllowed", "isAllowed", "isAllowed"]
[[3, 10], ["alice", 1], ["alice", 2], ["alice", 3], ["alice", 4], ["bob", 4], ["alice", 11]]
```

**Output**

```
[null, true, true, true, false, true, true]
```

**Explanation**

```
RateLimiter rateLimiter = new RateLimiter(3, 10); // 3 requests per 10 seconds, per user

rateLimiter.isAllowed("alice", 1);   // returns true,  alice has 1 request in the window
rateLimiter.isAllowed("alice", 2);   // returns true,  alice has 2 requests in the window
rateLimiter.isAllowed("alice", 3);   // returns true,  alice has 3 requests in the window
rateLimiter.isAllowed("alice", 4);   // returns false, alice is at her limit of 3
rateLimiter.isAllowed("bob", 4);     // returns true,  bob has his own independent quota
rateLimiter.isAllowed("alice", 11);  // returns true,  the request at t = 1 has expired
```

---

## Example 2

**Input**

```
["RateLimiter", "isAllowed", "isAllowed", "isAllowed", "isAllowed"]
[[1, 5], ["carol", 1], ["carol", 3], ["carol", 5], ["carol", 6]]
```

**Output**

```
[null, true, false, false, true]
```

**Explanation**

```
RateLimiter rateLimiter = new RateLimiter(1, 5);

rateLimiter.isAllowed("carol", 1);   // returns true
rateLimiter.isAllowed("carol", 3);   // returns false, the request at t = 1 is still in the window
rateLimiter.isAllowed("carol", 5);   // returns false, the request at t = 1 is still in the window
rateLimiter.isAllowed("carol", 6);   // returns true,  the request at t = 1 has now expired
```

Note that the denied requests at `t = 3` and `t = 5` do not consume any quota, which is why the
request at `t = 6` succeeds.

---

## Constraints

- `1 <= maxRequests <= 10^4`
- `1 <= windowSize <= 10^5`
- `1 <= userId.length <= 20`
- `userId` consists of lowercase English letters and digits.
- `1 <= timestamp <= 10^9`
- Timestamps are passed in non-decreasing order.
- At most `10^5` calls will be made to `isAllowed`.

---

## Follow-up

1. Can you make `isAllowed` run in **amortized O(1)** time?
2. Users who stop making requests still occupy memory. How would you reclaim space for
   inactive users without breaking the amortized time bound?
3. How would your design change if each user could be assigned a **different** limit at runtime?


# Code:

```cpp

#include <bits/stdc++.h>
using namespace std;

class RateLimiter {
private:
    int maxRequests;   // e.g. 3
    int windowSize;    // e.g. 60 seconds
    unordered_map<string, queue<int>> log;  // user -> timestamps

public:
    RateLimiter(int maxRequests, int windowSize) {
        this->maxRequests = maxRequests;
        this->windowSize = windowSize;
    }

    bool isAllowed(string user, int timestamp) {
        queue<int>& times = log[user];   // creates empty queue if new user

        // evict everything that fell out of the window
        while (!times.empty() && times.front() <= timestamp - windowSize) {
            times.pop();
        }

        if (times.size() < maxRequests) {
            times.push(timestamp);
            return true;
        }
        return false;
    }
};

```
