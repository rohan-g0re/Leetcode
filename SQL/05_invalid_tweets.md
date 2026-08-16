# LC 1683 - Easy


### 1. Count the characters using underscores
- hence used 16 underscores which make sure that the string has 16 characters
- and then added % which means zero or more characters
- together they select strings with 16 or more characters

```sql

SELECT tweet_id 
FROM Tweets
WHERE content LIKE '________________%';

```

### 2. Using CHAR_LENGTH --> this counts number of ALPHANUMERIC CHARACTERS

```sql
SELECT tweet_id 
FROM Tweets
WHERE CHAR_LENGTH(content) > 15;
```


### 3. Using LENGTH --> THIS COUNTS UNICODE LENGTH --> 

```
SELECT tweet_id 
FROM Tweets
WHERE LENGTH(content) > 15;
```
# IMPORTANT NOTE: for this question its okay but if the content would have had emojis then we cannot use `LENGTH` since unicode for single emoji might be 4 or something else --> so we need to remember when to use this carefully