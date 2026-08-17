
# LC 1661 - Easy

## Attempt 1 - self join with lag

#### Intuition:
- difference with previous row
- sum up differences
- group by machine and process id
- group by with machine

```sql
SELECT
    machine_id,
    -- LAG(timestamp, 1) OVER (PARTITION BY machine_id ORDER BY timestamp) AS test
    timestamp - LAG(timestamp, 1) OVER (PARTITION BY machine_id ORDER BY timestamp) AS diff
FROM Activity
;
```
- did not complete since i did not get what i wanted
- In retrospection, I think I could have used the WHERE cases over here as well, just like attempted to

## Attempt 2 - It was easier to self join using start of one table and end of another

#### Intuition:

1. create start snapshot
2. create end snapshot
3. join on machine and process id
4. calculate diff
5. group by 
6. sum 
7. give it finally to avg



```sql
SELECT
    s.machine_id,
    e.machine_id,
    -- s.process_id,
    -- e.process_id,
    -- s.activity_type,
    -- e.activity_type,
    s.timestamp,
    e.timestamp, 
    e.timestamp - s.timestamp AS diff,
    SUM(e.timestamp - s.timestamp),
    AVG(e.timestamp - s.timestamp)
FROM Activity s
JOIN Activity e ON (s.machine_id, s.process_id) = (e.machine_id, e.process_id)
where s.activity_type = 'start' AND e.activity_type = 'end'
GROUP BY s.machine_id, s.process_id
;
```

- next steps included a GROUP BY again --> but can do double 
- So used this complete setup as **Inline Subquery**

# Attempt 3: - Used Attempt 2 as subquery 

```sql
*/
SELECT 

    DIFF_TABLE.machine_id, 
    ROUND(AVG(DIFF_TABLE.diff), 3) AS processing_time

FROM
    (    
        SELECT
            s.machine_id,
            s.process_id,
            e.timestamp - s.timestamp AS diff
        FROM Activity s
        JOIN Activity e ON (s.machine_id, s.process_id) = (e.machine_id, e.process_id)
        where s.activity_type = 'start' AND e.activity_type = 'end'
        GROUP BY s.machine_id, s.process_id
    ) AS DIFF_TABLE

GROUP BY DIFF_TABLE.machine_id;
```

# Learnings:
- **EVERY DERIVED TABLE NEEDS AN ALIAS** --> hence the intermediate table created by subquery needs an alias as well - And everything outside the subquery will reference that table with that alias --> over here its 'DIFF_TABLE'.



# Attempt 4: Final Optimization --> JOINING basically did the grouping - so dont need subquery

- hence i remove the subquery group by 
- hence no need of subquery --> As I did that because I could not do a double group by

```sql


SELECT 
    s.machine_id, 
    ROUND(AVG(e.timestamp - s.timestamp), 3) AS processing_time

FROM Activity s
JOIN Activity e ON (s.machine_id, s.process_id) = (e.machine_id, e.process_id)
where s.activity_type = 'start' AND e.activity_type = 'end'

GROUP BY s.machine_id;


```