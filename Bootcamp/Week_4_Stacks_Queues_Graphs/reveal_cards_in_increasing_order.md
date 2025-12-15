You are given an integer array deck. There is a deck of cards where every card has a unique integer. The integer on the ith card is deck[i].

You can order the deck in any order you want. Initially, all the cards start face down (unrevealed) in one deck.

You will do the following steps repeatedly until all cards are revealed:

1. Take the top card of the deck, reveal it, and take it out of the deck.
2. If there are still cards in the deck, put the next top card of the deck at the bottom of the deck.
3. If there are still unrevealed cards, go back to step 1. Otherwise, stop.

Return an ordering of the deck that would reveal the cards in increasing order.

Example 1:

Input: deck = [17,13,11,2,3,5,7]
Output: [2,13,3,11,5,17,7]
Explanation:
We get the deck in the order [17,13,11,2,3,5,7] (this order does not matter), and reorder it.
After reordering, the deck starts as [2,13,3,11,5,17,7], where 2 is the top of the deck.
We reveal 2, and move 13 to the bottom. The deck is now [3,11,5,17,7,13].
We reveal 3, and move 11 to the bottom. The deck is now [5,17,7,13,11].
We reveal 5, and move 17 to the bottom. The deck is now [7,13,11,17].
We reveal 7, and move 13 to the bottom. The deck is now [11,17,13].
We reveal 11, and move 17 to the bottom. The deck is now [13,17].
We reveal 13, and move 17 to the bottom. The deck is now [17].
We reveal 17.
Since all the cards revealed are in increasing order, the answer is correct.

Example 2:

Input: deck = [1,1000]
Output: [1,1000]

****************

## Intuition

- We need to find the order such that when we reveal cards following the pattern, they appear in increasing order
- Reverse simulation: work backwards from sorted deck
- Use queue/deque to simulate the reverse process
- Sort cards, then simulate reverse revealing pattern

## BRUTE FORCE --> Simulate Forward Process

- Try all possible orderings
- For each ordering, simulate the revealing process
- Check if revealed cards are in increasing order

TC --> O(n! * n) - too slow

## OPTIMAL --> Reverse Simulation with Queue

- Sort the deck in ascending order
- Simulate the reverse process using a queue/deque
- Start with indices in a queue
- For each card (from smallest to largest):
  - Place card at front index of queue
  - Remove that index
  - Move next index to back (simulating reverse of moving card to bottom)

```
class Solution {
public:
    vector<int> deckRevealedIncreasing(vector<int>& deck) {
        
        int n = deck.size();
        sort(deck.begin(), deck.end());
        
        deque<int> indexQueue;
        for (int i = 0; i < n; i++) {
            indexQueue.push_back(i);
        }
        
        vector<int> result(n);
        
        for (int card : deck) {
            // Place card at the front index
            result[indexQueue.front()] = card;
            indexQueue.pop_front();
            
            // Move next index to back (simulating reverse process)
            if (!indexQueue.empty()) {
                indexQueue.push_back(indexQueue.front());
                indexQueue.pop_front();
            }
        }
        
        return result;
    }
};
```

## ALTERNATIVE --> Reverse Simulation with Deque (Card Values)

- Sort deck
- Use deque to build result by simulating reverse
- Start from largest card, work backwards

```
class Solution {
public:
    vector<int> deckRevealedIncreasing(vector<int>& deck) {
        
        sort(deck.begin(), deck.end());
        deque<int> dq;
        
        // Process from largest to smallest
        for (int i = deck.size() - 1; i >= 0; i--) {
            if (!dq.empty()) {
                // Move last element to front (reverse of moving to bottom)
                dq.push_front(dq.back());
                dq.pop_back();
            }
            // Add current card to front
            dq.push_front(deck[i]);
        }
        
        return vector<int>(dq.begin(), dq.end());
    }
};
```

## TC --> O(n log n) for sorting + O(n) for simulation = O(n log n)
## SC --> O(n) for deque/queue and result array

