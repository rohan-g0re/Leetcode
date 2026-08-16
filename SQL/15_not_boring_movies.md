# LC 620 - Easy

- 'ORDER BY' defaults to ascending sort

```sql

SELECT * 
FROM Cinema
WHERE id % 2 != 0
AND description != 'boring'
ORDER BY rating DESC;
```