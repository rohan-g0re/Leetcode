# Approach 1: Spawn "isSameTree" logic when match 

## INTUITION:

1. keep going deep in main tree --> UNTIL val matches other_tree's root
2. when match, spawn "same_tree" logic on both those nodes

#### THIS IS VERY EXPENSIVE --> Time complexity: O(n×m)
- where (n) = number of nodes in root and (m) = number of nodes in subRoot.
- **In worst case, for each node in root, we compare up to all nodes in subRoot.**

## Code 1:

```cpp
class Solution {

    bool same_tree(TreeNode* p, TreeNode* q) {

        // ------ BASE CASES ------ 

        // 1. if both are null --> same tree
        if( p == nullptr && q == nullptr) return true;
        
        // 2. if one of them is null --> FAILED MATCH
        if( p == nullptr || q == nullptr) return false;
        // TECHNICALLY this could execute even if both are nulls --> but we ended up here bcoz first base case did not execute
        
        // 3. if values mismatch --> FAILED
        if( p -> val != q -> val) return false;


        // ----- MAIN LOGIC -----

        // the function compares 2 nodes --> therefore we need to spawn on left child of p and q together -- and on right child of p and q as well
        
        return (same_tree( p -> left, q -> left) && same_tree( p -> right, q -> right));

        // we "AND" it because --> we return true if Both subtrees match
        
    }


    bool preorder(TreeNode* root, TreeNode* subroot){

        if(root == nullptr) return false;

        // 1. match --> spawn
        if(root -> val == subroot -> val){
            if(same_tree(root, subroot)){
                return true;
            }
        }

        // 2. no match --> explore children
        return (preorder(root -> left, subroot) || preorder(root -> right, subroot) );

        // "OR" because we return true if there was a macth in either of the sub-trees
    }

public:
    bool isSubtree(TreeNode* root, TreeNode* subRoot) {

        // 1. spawn dfs on root

        return preorder(root, subRoot);
        
    }
};
```



# Approach 2: Tree Serialization

## INTUITION:

1. **Idea** --> turn each tree into a unique string --> then subtree check becomes a substring check
2. **Why null markers (`N`) matter** --> without them, different shapes can serialize to the same string --> we need structure in the string, not just values
3. **ACTUAL WAY** --> preorder serialize both trees --> if `subRoot` string is found inside `root` string --> return true

#### Example

```
root    = [3,4,5,1,2]
subRoot = [4,1,2]
```

Serialization:

```
root:    (3,(4,(1,N,N),(2,N,N)),(5,N,N))
subRoot: (4,(1,N,N),(2,N,N))
```

if `subRoot` serialization is a **substring** of `root` serialization --> return `true`.


## Code 2: 

```cpp
class Solution {
private:
    string serialize(TreeNode* node) {
        if (!node) return "N";
        return "(" + to_string(node->val) + "," + serialize(node->left) + "," + serialize(node->right) + ")";
    }

public:
    bool isSubtree(TreeNode* root, TreeNode* subRoot) {
        string rootSerialized = serialize(root);
        string subRootSerialized = serialize(subRoot);
        return rootSerialized.find(subRootSerialized) != string::npos;
    }
};
```