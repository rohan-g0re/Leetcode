# LC 1581 - Easy


Real answer: nobody writes it top-to-bottom. You build it **outward from `FROM`**, running it at each step and looking at the output. Each step is a valid runnable query, and each one answers a smaller question.

## The build

**Step 0 — say the sentence.** "Visits that have no matching transaction, counted per customer." That sentence dictates everything below.

**Step 1 — get the tables together. Nothing else.**
```sql
SELECT *
FROM Visits v
LEFT JOIN Transactions t ON v.visit_id = t.visit_id;
```
`SELECT *` on purpose — you want to *see* the shape. You look at it and observe the `NULL` rows. Say out loud: "I need visits with no transaction, so I lead with Visits and `LEFT JOIN`, which keeps the unmatched ones."

**Step 2 — filter to just what you care about.**
```sql
SELECT *
FROM Visits v
LEFT JOIN Transactions t ON v.visit_id = t.visit_id
WHERE t.transaction_id IS NULL;
```
Now the output *is* the answer, just not aggregated yet. This is the checkpoint that matters — if this row set is right, the rest is mechanical.

**Step 3 — aggregate.**
```sql
SELECT v.customer_id, COUNT(*) AS count_no_trans
FROM Visits v
LEFT JOIN Transactions t ON v.visit_id = t.visit_id
WHERE t.transaction_id IS NULL
GROUP BY v.customer_id;
```
"Now one row per customer, counting the rows in each pile."

**Step 4 — clean up.** Fix column names to match the spec, add `ORDER BY` if asked.

## The general order

Build in **execution order**, not writing order:

```
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY
```

Which is exactly the list from before — it's not just a mental model, it's the construction sequence. `SELECT` is filled in **last** (keep it as `*` until the end), because you can't know what to display until you know what a row represents.

# Leanrings

1. ANTI-JOIN pattern:
    - Basically when we perform a join but want the 'failing rows - rows which DONT HAVE all values and have some NULLS'

2. Useful habbit: **State the alternative you rejected.** "I could do `NOT IN (SELECT visit_id FROM Transactions)`, but that breaks if the subquery returns `NULL`s, so I'd rather use the `LEFT JOIN`." One sentence, and it proves you chose rather than pattern-matched.

Nobody can tell whether you knew the anti-join pattern in advance — most experienced people do. What they can tell is whether you can explain what each clause does to the row set. Build it in layers, and that explanation comes for free.