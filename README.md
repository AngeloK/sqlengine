# A small wrapper of MySQLdb

###Usage:

decorator:

* @with_connection
* @with_transaction

method:

* insert(sql, *args)
* update(sql, *args)
* select(sql, *args)
* select_one(sql, *arge)
* delete(sql, *args)


###Getting start

```
create_engine(host="localhost", port=3306, user="root", password="root")
```


Create a mysql connection engine, which could be used for adding new connection,and then, enjoy it.

###Example

```python
@with_transaction
def start_transaction():
	transaction1()
	transaction2()
	transaction3()
```

With this decorator, we could create an transaction (or nest into another transaction), the acions in those transactions will not be commited until every statement used correctly, or rolled back in the end.

###Some test log


```
2015-05-21 12:33:59,690 - INFO: Create engine with params:
{'passwd': '', 'host': 'localhost', 'db': 'testdb', 'user': 'root', 'port': 3306}
2015-05-21 12:33:59,690 - INFO: Initialize a lazy connection in local thread 0x10ebe3510
2015-05-21 12:33:59,690 - INFO: begin transaction...
2015-05-21 12:33:59,691 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged', 2)
2015-05-21 12:33:59,728 - INFO: New connection 0x7fe74a052420
2015-05-21 12:33:59,729 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged', 1)
2015-05-21 12:33:59,729 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged1', 2)
2015-05-21 12:33:59,730 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged1', 1)
2015-05-21 12:33:59,730 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged2', 2)
2015-05-21 12:33:59,730 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged2', 1)
2015-05-21 12:33:59,730 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged3', 2)
2015-05-21 12:33:59,731 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged3', 1)

====================
2015-05-21 12:33:59,731 - INFO: join current transaction...
2015-05-21 12:33:59,731 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged', 2)
2015-05-21 12:33:59,731 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged', 1)
2015-05-21 12:33:59,731 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged1', 2)
2015-05-21 12:33:59,732 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged1', 1)
2015-05-21 12:33:59,732 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged2', 2)
2015-05-21 12:33:59,732 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged2', 1)
2015-05-21 12:33:59,732 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged3', 2)
2015-05-21 12:33:59,733 - INFO: Going to execute SQL:UPDATE users SET name=%s where id=%s, Args:('newChanged3', 1)
2015-05-21 12:33:59,733 - INFO: Commited
2015-05-21 12:33:59,733 - INFO: Connection 0x7fe74a052420 closed!
2015-05-21 12:33:59,734 - INFO: Going to executing SQL:SELECT * FROM users where id=%s, Args:(1,)
2015-05-21 12:33:59,734 - INFO: New connection 0x7fe74902c020
2015-05-21 12:33:59,735 - INFO: Executing SQL:SELECT * FROM users where id=%s
[{'fullname': 'world', 'password': '123', 'id': 1L, 'name': 'newChanged3'}]
```


Not end...
