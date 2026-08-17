# LC 1068 - Easy

#### New learnings/Understandings:
    - I can use just `JOIN` instead of `INNER JOIN` --> also meaning that Join defaults to inner join
    - When doin Inner Join on 2 tables --> **we dont care about the order of tables**


```sql
SELECT Product.product_name, Sales.year, Sales.price
FROM Sales
INNER JOIN Product
ON Sales.product_id = Product.product_id;
```