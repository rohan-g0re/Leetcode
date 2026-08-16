# LC 1148 - Easy

- Used 'Alias' concept because the result wanted different column name
- Used 'ORDER BY' for sorting --> **FOR THE LAST LINE** i can use both column names for sorting:
    - author_id (original col name)
    - id (alias created)



# Code:

```sql

SELECT DISTINCT author_id AS id
FROM Views
WHERE author_id = viewer_id
ORDER BY id;

```