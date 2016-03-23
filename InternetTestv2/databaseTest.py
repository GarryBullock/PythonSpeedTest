import sqlite3 as sql

db = sql.connect('data/sqlite3.db')
#db = sql.connect(':memory:')

cursor = db.cursor()
#cursor.execute('''CREATE TABLE tweets(id INTEGER PRIMARY KEY, down INTEGER,
#                  up INTEGER, date TEXT)''')
#db.commit()

id = 1
down = 5
up = 10
date = '21/03/2016,14:08'
#cursor.execute('''INSERT INTO tweets(id, down, up, date)
#                  VALUES(?,?,?,?)''', (id,down,up,date))
#db.commit()

cursor.execute('''SELECT id, down, up, date FROM tweets''')
for row in cursor:
    print(row)
db.close()
print("finished")
