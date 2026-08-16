# Leetcode 1757

1. using simple select

```sql
SELECT product_id from Products
WHERE low_fats = 'Y' 
AND recyclable = 'Y';
```

2. Using row constuctor to compare both values in the same time

```sql

SELECT product_id from Products
WHERE (low_fats, recyclable) = ('Y', 'Y');
```

3. Using IN keyword

```sql

SELECT product_id from Products
WHERE (low_fats, recyclable) IN (('Y', 'Y'));
```