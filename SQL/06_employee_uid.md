# LC 1378 - Easy


- I need to show all the emplyee names - whether they have the uid or not --> hence whichever outer join i choose: employees table should be the one which falls on the "SIDE" of join

- The order of SELECT-ed columns is chosen for the output

- I can list all the columns initially in the select bcoz it is going to run in the end after all the joins



## 1. Using Left Outer Join

```sql

SELECT EmployeeUNI.unique_id, Employees.name
FROM Employees
LEFT JOIN EmployeeUNI
ON Employees.id = EmployeeUNI.id;

```


## 2. Using Right Outer Join

```sql

SELECT EmployeeUNI.unique_id, Employees.name
FROM EmployeeUNI
RIGHT JOIN Employees
ON EmployeeUNI.id = Employees.id;

```