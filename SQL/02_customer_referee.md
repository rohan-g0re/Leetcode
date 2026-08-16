# LC 584 - Easy


1. easy brute force logic

```sql

SELECT name from Customer
WHERE referee_id != 2
OR referee_id IS NULL;

```

2. Better:

```sql

SELECT name from Customer
WHERE referee_id != 2 
OR referee_id IS NULL;

```