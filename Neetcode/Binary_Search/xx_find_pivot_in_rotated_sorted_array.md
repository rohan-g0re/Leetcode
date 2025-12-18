# Find Pivot in Rotated Sorted Array

## What is a Pivot?

The **pivot** is the index where the array was rotated. In a rotated sorted array, the pivot is typically the **index of the minimum element** (the point where the array "breaks").

### Example:
```
Original: [0, 1, 2, 3, 4, 5, 6, 7]
Rotated:  [4, 5, 6, 7, 0, 1, 2, 3]
                    ↑
                 Pivot at index 4 (minimum element = 0)
```

---

## INTUITION: Based on Search in Rotated Sorted Array Logic

From the search problems, we learned:
- **If `nums[low] <= nums[mid]`**: Left part is sorted
- **If `nums[mid] <= nums[high]`**: Right part is sorted

For finding the pivot, we use a similar elimination strategy:
- **Compare `nums[mid]` with `nums[high]`** (or `nums[low]`)
- This tells us which half contains the pivot

---

## KEY INSIGHT: Compare with `nums[high]`

### Why `nums[high]`?
- In a rotated sorted array, the **rightmost element** helps us determine where the rotation occurred
- If `nums[mid] > nums[high]`: The pivot is definitely in the **right half** (mid+1 to high)
- If `nums[mid] < nums[high]`: The pivot is in the **left half** (low to mid, **including mid**)

### Logic:
```
If nums[mid] > nums[high]:
    → Right half is NOT sorted properly
    → Pivot must be in right half
    → Search in [mid+1, high]

If nums[mid] < nums[high]:
    → Right half IS sorted
    → Pivot is in left half (including mid itself!)
    → Search in [low, mid]
```

---

## SOLUTION 1: Find Minimum Element (Pivot Index) - No Duplicates

```cpp
class Solution {
public:
    int findMin(vector<int>& nums) {
        
        int low = 0;
        int high = nums.size() - 1;
        
        while (low < high) {  // Note: < not <=
            
            int mid = low + (high - low) / 2;
            
            // Compare with rightmost element
            if (nums[mid] > nums[high]) {
                // Pivot is in right half
                low = mid + 1;
            }
            else {
                // Pivot is in left half (including mid)
                high = mid;  // Note: NOT mid - 1
            }
        }
        
        // When low == high, we found the pivot
        return nums[low];  // or return low for index
    }
};
```

### Why `low < high` instead of `low <= high`?
- We want to stop when `low == high` (found the pivot)
- With `<=`, we'd need an extra check to avoid infinite loop
- With `<`, the loop naturally stops when `low == high`

### Why `high = mid` instead of `high = mid - 1`?
- When `nums[mid] < nums[high]`, the pivot could be **at mid itself**
- We must include `mid` in our search range
- Setting `high = mid - 1` would skip the actual pivot!

---

## SOLUTION 2: Find Pivot Index (Return Index, Not Value)

```cpp
class Solution {
public:
    int findPivotIndex(vector<int>& nums) {
        
        int low = 0;
        int high = nums.size() - 1;
        
        while (low < high) {
            
            int mid = low + (high - low) / 2;
            
            if (nums[mid] > nums[high]) {
                // Pivot is in right half
                low = mid + 1;
            }
            else {
                // Pivot is in left half (including mid)
                high = mid;
            }
        }
        
        return low;  // or return high (they're equal)
    }
};
```

---

## SOLUTION 3: Handle Duplicates (Similar to Problem II)

When duplicates exist, we need the same edge case handling:

```cpp
class Solution {
public:
    int findMin(vector<int>& nums) {
        
        int low = 0;
        int high = nums.size() - 1;
        
        while (low < high) {
            
            int mid = low + (high - low) / 2;
            
            // Handle duplicates: can't determine which half
            if (nums[mid] == nums[high]) {
                // Shrink from both ends
                high--;
            }
            else if (nums[mid] > nums[high]) {
                // Pivot in right half
                low = mid + 1;
            }
            else {
                // Pivot in left half (including mid)
                high = mid;
            }
        }
        
        return nums[low];
    }
};
```

